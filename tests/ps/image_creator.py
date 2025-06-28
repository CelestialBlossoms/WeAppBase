from PIL import Image, ImageDraw, ImageFont
import os

def create_image_with_text(configs, output_path):
    """
    通过在背景模板上绘制文本来生成图像。

    Args:
        configs (dict): 包含配置的字典。
            'background': 背景图片的路径。
            'elements': 要绘制的文本元素列表。
        output_path (str): 保存最终图像的路径。

    'elements'中的每个元素都应该是一个字典:
        {
            "text": "你的文本",
            "font_path": "path/to/font.ttf",
            "font_size": 50,
            "color": "#RRGGBB" or (R, G, B),
            "position": (x, y)  # 文本左上角的坐标
        }
    """
    try:
        # 加载背景图片
        background_image = Image.open(configs['background']).convert("RGBA")
        
        # 创建一个绘图上下文
        draw = ImageDraw.Draw(background_image)

        # 绘制每个文本元素
        for element in configs.get('elements', []):
            text = element['text']
            font_path = element['font_path']
            font_size = element['font_size']
            color = element['color']
            position = element['position']

            # 加载字体
            if not os.path.exists(font_path):
                print(f"错误: 字体文件未找到 {font_path}")
                continue
            font = ImageFont.truetype(font_path, font_size)

            # 绘制文本
            draw.text(position, text, font=font, fill=color)
            print(f"在 {position} 绘制了文本 '{text}'")

        # 保存最终图像
        background_image.save(output_path, "PNG")
        print(f"成功创建图像: {output_path}")

    except FileNotFoundError:
        print(f"错误: 背景图片未找到 {configs['background']}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == '__main__':
    # --- 您需要在此处进行配置 ---

    # 1. 提供您的背景图片（不含文字）的路径。
    #    重要提示：在Photoshop中删除文字图层，然后另存为PNG。
    background_file = 'background.png'  # 假设图片和脚本在同一目录

    # 2. 提供您的字体文件的路径。
    #    重要提示：将.ttf或.otf字体文件复制到您的项目目录中。
    simhei_font_path = 'SimHei.ttf'      # 例如，瓶身上的字体
    yahei_font_path = 'msyh.ttc'         # 例如，包装盒上的字体（微软雅黑可能是.ttc文件）

    # 3. 定义文本、属性及其精确位置。
    #    如何找到位置(x, y)坐标:
    #    在图像编辑器（如Photoshop, GIMP, 甚至Windows画图）中打开您的background.png。
    #    将光标移动到您希望文本左上角开始的位置。
    #    编辑器通常会显示光标的(x, y)像素坐标。请使用这些值。
    #    这可能需要一些反复试验才能达到完美效果！

    image_configs = {
        "background": background_file,
        "elements": [
            # --- 瓶身上的文字 ---
            {
                "text": "天",
                "font_path": simhei_font_path,
                "font_size": 150,         # 估算值，请自行调整
                "color": "#FF0000",       # 红色，来自您最初的配置
                "position": (250, 400)    # 估算值，请务必替换为真实坐标
            },
            {
                "text": "地",
                "font_path": simhei_font_path,
                "font_size": 150,         # 估算值，请自行调整
                "color": "#0000FF",       # 蓝色，来自您最初的配置
                "position": (250, 600)    # 估算值，请务必替换为真实坐标
            },
            # --- 包装盒上的文字（根据需要添加） ---
            # {
            #     "text": "天",
            #     "font_path": yahei_font_path,
            #     "font_size": 180,
            #     "color": "#000000",
            #     "position": (750, 300)
            # },
        ]
    }

    # --- 生成图像 ---
    if not os.path.exists(background_file) or not os.path.exists(simhei_font_path):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! 需要操作：请先完成上面的配置部分。                      !!!")
        print("!!! 1. 设置 'background_file' 的正确路径。                  !!!")
        print("!!! 2. 设置字体文件的正确路径。                           !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        create_image_with_text(image_configs, 'final_output.png') 