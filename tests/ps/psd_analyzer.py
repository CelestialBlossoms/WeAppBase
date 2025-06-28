from psd_tools import PSDImage
import json
from pathlib import Path

def analyze_psd_structure(psd_path):
    """
    分析PSD文件的图层结构
    
    Args:
        psd_path (str): PSD文件路径
    """
    print(f"正在分析PSD文件: {psd_path}")
    print("=" * 60)
    
    try:
        # 加载PSD文件
        psd = PSDImage.open(psd_path)
        
        # 显示PSD基本信息
        print(f"PSD尺寸: {psd.width} x {psd.height} 像素")
        print(f"颜色模式: {psd.color_mode}")
        
        # 计算总图层数
        try:
            all_layers = list(psd.descendants)
            total_layers = len(all_layers)
        except:
            total_layers = "无法计算"
        
        print(f"总图层数: {total_layers}")
        print("=" * 60)
        
        # 递归分析所有图层
        layer_info = []
        
        def analyze_layer(layer, depth=0):
            indent = "  " * depth
            layer_data = {
                "name": layer.name,
                "kind": layer.kind,
                "visible": layer.visible,
                "depth": depth
            }
            
            print(f"{indent}📁 图层: '{layer.name}' (类型: {layer.kind})")
            
            # 获取图层位置和尺寸
            try:
                if hasattr(layer, 'bbox') and layer.bbox:
                    bbox = layer.bbox
                    layer_data["bbox"] = {
                        "left": bbox.x1,
                        "top": bbox.y1, 
                        "right": bbox.x2,
                        "bottom": bbox.y2,
                        "width": bbox.x2 - bbox.x1,
                        "height": bbox.y2 - bbox.y1
                    }
                    print(f"{indent}   📏 位置: ({bbox.x1}, {bbox.y1}) - ({bbox.x2}, {bbox.y2})")
                    print(f"{indent}   📐 尺寸: {bbox.x2 - bbox.x1} x {bbox.y2 - bbox.y1}")
            except Exception as e:
                print(f"{indent}   ⚠️  无法获取位置信息: {e}")
            
            # 如果是文本图层，获取详细信息
            if layer.kind == 'type':
                try:
                    text_content = layer.text
                    print(f"{indent}   🔤 文本内容: '{text_content}'")
                    layer_data["text"] = text_content
                    
                    # 尝试获取字体信息
                    try:
                        if hasattr(layer, 'engine_dict'):
                            engine_dict = layer.engine_dict
                            
                            # 提取字体信息
                            if 'StyleRun' in engine_dict:
                                for i, style_run in enumerate(engine_dict['StyleRun']['RunArray']):
                                    style_sheet = style_run['StyleSheet']['StyleSheetData']
                                    print(f"{indent}   📝 样式 {i+1}:")
                                    
                                    # 字体大小
                                    if 'FontSize' in style_sheet:
                                        font_size = style_sheet['FontSize']
                                        print(f"{indent}      字号: {font_size}")
                                        layer_data["font_size"] = str(font_size)
                                    
                                    # 字体名称
                                    if 'FontName' in style_sheet:
                                        font_name = style_sheet['FontName']
                                        print(f"{indent}      字体: {font_name}")
                                        layer_data["font_name"] = str(font_name)
                                    
                                    # 颜色信息
                                    if 'FillColor' in style_sheet:
                                        fill_color = style_sheet['FillColor']
                                        if 'Values' in fill_color:
                                            color_values = fill_color['Values']
                                            if len(color_values) >= 3:
                                                # 转换为16进制颜色
                                                r = int(float(color_values[0]) * 255)
                                                g = int(float(color_values[1]) * 255) 
                                                b = int(float(color_values[2]) * 255)
                                                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                                                print(f"{indent}      颜色: {hex_color}")
                                                layer_data["color"] = hex_color
                                    
                    except Exception as e:
                        print(f"{indent}   ⚠️  读取文本样式时出错: {e}")
                        
                except Exception as e:
                    print(f"{indent}   ⚠️  读取文本内容时出错: {e}")
            
            # 显示可见性
            print(f"{indent}   👁️  可见: {'是' if layer.visible else '否'}")
            
            layer_info.append(layer_data)
            
            # 如果是图层组，递归处理子图层
            if layer.kind == 'group':
                try:
                    child_layers = list(layer)
                    print(f"{indent}   📂 包含 {len(child_layers)} 个子图层:")
                    for child in child_layers:
                        analyze_layer(child, depth + 1)
                except Exception as e:
                    print(f"{indent}   ⚠️  无法遍历子图层: {e}")
            
            print()  # 空行分隔
        
        # 分析所有顶层图层
        print("🔍 图层结构分析:")
        print("-" * 60)
        
        try:
            # 尝试不同的迭代方法
            top_layers = list(psd)
            for layer in top_layers:
                analyze_layer(layer)
        except Exception as e:
            print(f"⚠️  无法遍历顶层图层: {e}")
            try:
                # 尝试另一种方法
                if hasattr(psd, '_layers'):
                    for layer in psd._layers:
                        analyze_layer(layer)
            except Exception as e2:
                print(f"⚠️  备用方法也失败: {e2}")
        
        # 保存分析结果到JSON文件
        output_file = "psd_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "psd_info": {
                    "width": psd.width,
                    "height": psd.height,
                    "color_mode": str(psd.color_mode),
                    "total_layers": total_layers
                },
                "layers": layer_info
            }, f, ensure_ascii=False, indent=2)
        
        print("=" * 60)
        print(f"✅ 分析完成！详细信息已保存到: {output_file}")
        print("\n💡 下一步建议:")
        print("1. 查看上面的文本图层，确定哪些需要动态修改")
        print("2. 在Photoshop中将这些图层重命名为 'dynamic_text_xxx' 格式")
        print("3. 然后运行模板生成器脚本")
        
    except Exception as e:
        print(f"❌ 分析PSD文件时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # PSD文件路径
    psd_file_path = r"D:\code\company\mini_code\金酱psd\PSD.psd"
    
    # 检查文件是否存在
    if not Path(psd_file_path).exists():
        print(f"❌ 错误: 找不到PSD文件 {psd_file_path}")
        print("请检查文件路径是否正确。")
    else:
        analyze_psd_structure(psd_file_path) 