from psd_tools import PSDImage
from psd_tools.api.layers import TypeLayer, Group
from psd_tools.psd.engine_data import String, Float, List as EngineList
import json


def process_text_layers(psd_path, output_path, config):
    """
    处理PSD文件中的文本图层

    参数:
    psd_path: 输入的PSD文件路径
    output_path: 输出的PSD文件路径
    config: 包含替换规则的配置列表
    """
    # 加载PSD文件
    psd = PSDImage.open(psd_path)

    # 递归处理所有图层
    def process_layer(layer):
        # 处理文本图层
        if layer.kind == 'type':
            # 应用所有替换规则
            for rule in config:
                if rule['oldText'] in layer.text:
                    # 执行文本替换
                    new_text = layer.text.replace(rule['oldText'], rule['newText'])

                    # 更新文本: 我们必须修改底层的 engine_dict 并使用正确的 psd-tools 类型.
                    print("layer.engine_dict['Editor']['Text']",layer.engine_dict['Editor']['Text'],String(new_text))
                    layer.engine_dict['Editor']['Text'] = String(new_text)
                    print(f"Replaced text: '{rule['oldText']}' with '{new_text}'")

                    # 要应用样式更改，我们还需要修改 engine_dict
                    if 'StyleRun' in layer.engine_dict:
                        for style_run in layer.engine_dict['StyleRun']['RunArray']:
                            style_sheet = style_run['StyleSheet']['StyleSheetData']

                            # 设置字体
                            if 'font' in rule:
                                # Font modification via engine_dict is complex and not implemented here.
                                print(f"Font setting is complex. Skipping font change to: {rule['font']}")

                            # 设置字号
                            if 'size' in rule:
                                style_sheet['FontSize'] = Float(rule['size'])
                                print(f"Set font size to: {rule['size']}")

                            # 设置颜色
                            if 'color' in rule:
                                # 将十六进制颜色转换为RGB值
                                hex_color = rule['color'].lstrip('#')
                                rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
                                # 转换为0-1范围的浮点数
                                normalized_rgba = tuple(c / 255.0 for c in rgb) + (1.0,)  # 添加alpha通道
                                if 'FillColor' not in style_sheet:
                                    # This is complex to create from scratch.
                                    # For now, we only modify existing colors.
                                    print("Skipping color change because 'FillColor' is not defined for this text.")
                                    continue
                                color_values = [Float(c) for c in normalized_rgba]
                                style_sheet['FillColor']['Values'] = EngineList(color_values)
                                print(f"Set color to: {rule['color']}")

        # 递归处理子图层（图层组）
        if layer.kind == 'group':
            for child in layer:
                process_layer(child)

    # 处理所有顶层图层
    for layer in psd:
        process_layer(layer)

    # 保存修改后的PSD
    psd.save(output_path)
    print(f"Saved modified PSD to: {output_path}")


def save_psd_as_png(psd_path, png_path):
    """
    Composites a PSD file and saves it as a PNG.

    Args:
        psd_path (str): The path to the input PSD file.
        png_path (str): The path to save the output PNG file.
    """
    try:
        psd = PSDImage.open(psd_path)
        composite_image = psd.composite()
        composite_image.save(png_path)
        print(f"Successfully converted {psd_path} to {png_path}")
    except Exception as e:
        print(f"An error occurred during PNG conversion: {e}")


# 示例配置
config = [
    {
        "oldText": "金",
        "newText": "天",
        "font": "SimHei",  # 中文字体示例
        "size": 36,  # 字号（单位与PSD中相同）
        "color": "#FF0000"  # 红色
    },
    {
        "oldText": "酱",
        "newText": "地",
        "font": "Microsoft YaHei",
        "size": 32,
        "color": "#0000FF"  # 蓝色
    }
]

# 使用示例
if __name__ == "__main__":
    # 从JSON文件加载配置（可选）
    # with open('config.json') as f:
    #     config = json.load(f)

    output_psd_path = 'output.psd'
    process_text_layers(
        psd_path=r'D:\code\py3Test\PS\ps_script\jinjiang2.psd',
        output_path=output_psd_path,
        config=config
    )

    # Convert the output PSD to a PNG to verify the result
    save_psd_as_png(output_psd_path, 'output.png')
