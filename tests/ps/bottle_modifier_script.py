#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金酱酒瓶图片修改脚本
功能：在指定区域添加文字，生成个性化酒瓶
"""

import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import argparse

# 配置信息
BOTTLE_CONFIG = {
    "image_info": {
        "name": "金酱.png",
        "width": 560,
        "height": 373
    },
    "text_regions": [
        {"id": 1, "x": 201, "y": 187, "width": 26, "height": 27, "name": "上部标签"},
        {"id": 2, "x": 202, "y": 240, "width": 27, "height": 26, "name": "下部标签"},
        {"id": 3, "x": 313, "y": 118, "width": 25, "height": 27, "name": "右上区域"},
        {"id": 4, "x": 315, "y": 177, "width": 27, "height": 24, "name": "右下区域"}
    ]
}


class BottleModifier:
    """酒瓶修改器类"""

    def __init__(self, image_path="金酱.png"):
        self.image_path = image_path
        self.config = BOTTLE_CONFIG
        self.base_image = None
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

        # 验证图片文件存在
        if not Path(image_path).exists():
            raise FileNotFoundError(f"找不到图片文件: {image_path}")

        # 加载图片
        self.load_image()

    def load_image(self):
        """加载底图"""
        try:
            self.base_image = Image.open(self.image_path).convert('RGBA')
            print(f"✅ 成功加载图片: {self.image_path}")
            print(f"   图片尺寸: {self.base_image.size}")
        except Exception as e:
            raise Exception(f"加载图片失败: {e}")

    def get_font(self, font_size=12, font_family="default"):
        """获取字体"""
        font_paths = {
            "default": None,
            "arial": [
                "/System/Library/Fonts/Arial.ttf",  # macOS
                "C:/Windows/Fonts/arial.ttf",  # Windows
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Linux
            ],
            "chinese": [
                "/System/Library/Fonts/PingFang.ttc",  # macOS
                "C:/Windows/Fonts/msyh.ttc",  # Windows YaHei
                "C:/Windows/Fonts/simhei.ttf",  # Windows SimHei
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"  # Linux
            ]
        }

        if font_family == "default":
            return ImageFont.load_default()

        # 尝试加载指定字体
        for font_path in font_paths.get(font_family, []):
            if font_path and Path(font_path).exists():
                try:
                    return ImageFont.truetype(font_path, font_size)
                except:
                    continue

        # 备用字体
        print(f"⚠️ 无法加载字体 {font_family}，使用默认字体")
        return ImageFont.load_default()

    def create_text_image(self, text, region_id, font_size=20, font_color="#000000", font_family="chinese"):
        """
        创建透明背景的文字图片 - 优化版本

        Args:
            text: 文字内容
            region_id: 区域ID
            font_size: 字体大小 (默认20，比之前更大)
            font_color: 字体颜色
            font_family: 字体类型

        Returns:
            PIL Image对象
        """
        # 获取区域信息
        region = self.get_region(region_id)
        if not region:
            raise ValueError(f"未找到区域 {region_id}")

        width = region["width"]
        height = region["height"]

        # 自动调整字体大小以适应区域
        auto_font_size = min(width, height) - 4  # 留4像素边距
        if font_size > auto_font_size:
            font_size = auto_font_size
            print(f"🔧 区域{region_id}字体自动调整为: {font_size}")

        # 创建透明图片
        text_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_img)

        # 获取字体
        font = self.get_font(font_size, font_family)

        # 多次尝试找到合适的字体大小
        for attempt in range(5):
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 如果文字太大，缩小字体
            if text_width > width - 2 or text_height > height - 2:
                font_size = max(8, font_size - 2)
                font = self.get_font(font_size, font_family)
                print(f"🔧 区域{region_id}字体缩小为: {font_size}")
            else:
                break

        # 计算文字位置 - 居中
        x = max(0, (width - text_width) // 2)
        y = max(0, (height - text_height) // 2)

        # 绘制文字
        draw.text((x, y), text, font=font, fill=font_color)

        return text_img

    def get_region(self, region_id):
        """获取区域信息"""
        for region in self.config["text_regions"]:
            if region["id"] == region_id:
                return region
        return None

    def add_text_to_region(self, text, region_id, **style_options):
        """
        在指定区域添加文字

        Args:
            text: 文字内容
            region_id: 区域ID
            **style_options: 样式选项 (font_size, font_color, font_family)
        """
        region = self.get_region(region_id)
        if not region:
            print(f"❌ 未找到区域 {region_id}")
            return False

        # 默认样式 - 增大字体
        default_style = {
            "font_size": 20,  # 从12增加到20
            "font_color": "#000000",
            "font_family": "chinese"
        }
        default_style.update(style_options)

        try:
            # 创建文字图片
            text_img = self.create_text_image(text, region_id, **default_style)

            # 叠加到底图
            position = (region["x"], region["y"])
            self.base_image.paste(text_img, position, text_img)

            print(f"✅ 已添加文字 '{text}' 到{region['name']} (区域{region_id})")
            return True

        except Exception as e:
            print(f"❌ 添加文字失败: {e}")
            return False

    def batch_add_texts(self, text_configs):
        """
        批量添加文字

        Args:
            text_configs: 文字配置列表
            [
                {"region_id": 1, "text": "金", "font_color": "#FFD700"},
                {"region_id": 2, "text": "酱", "font_size": 14}
            ]
        """
        success_count = 0

        for config in text_configs:
            region_id = config.pop("region_id")
            text = config.pop("text")

            if self.add_text_to_region(text, region_id, **config):
                success_count += 1

        print(f"\n📊 批量添加完成: {success_count}/{len(text_configs)} 个文字添加成功")
        return success_count

    def save_result(self, output_path=None, format="PNG"):
        """保存修改后的图片"""
        if not output_path:
            timestamp = Path().resolve().name
            output_path = self.output_dir / f"定制酒瓶_{timestamp}.png"

        try:
            self.base_image.save(output_path, format)
            print(f"💾 图片已保存: {output_path}")
            return str(output_path)
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return None

    def reset_image(self):
        """重置图片到原始状态"""
        self.load_image()
        print("🔄 图片已重置到原始状态")

    def preview_regions(self, output_path=None):
        """生成区域标注预览图"""
        preview_img = self.base_image.copy()
        draw = ImageDraw.Draw(preview_img)

        for region in self.config["text_regions"]:
            # 绘制区域框
            x, y = region["x"], region["y"]
            w, h = region["width"], region["height"]

            # 红色边框
            draw.rectangle([x, y, x + w, y + h], outline="#FF0000", width=2)

            # 标签
            label = f"区域{region['id']}"
            draw.text((x, y - 15), label, fill="#FF0000")

        if not output_path:
            output_path = self.output_dir / "区域预览.png"

        preview_img.save(output_path)
        print(f"🔍 区域预览已保存: {output_path}")
        return str(output_path)

    def show_regions_info(self):
        """显示区域信息"""
        print("\n📍 可用的文字区域:")
        print("-" * 50)
        for region in self.config["text_regions"]:
            print(f"区域 {region['id']}: {region['name']}")
            print(f"   位置: ({region['x']}, {region['y']})")
            print(f"   尺寸: {region['width']} x {region['height']}")
            print()


def main():
    """主函数 - 命令行界面"""
    parser = argparse.ArgumentParser(description="金酱酒瓶图片修改工具")
    parser.add_argument("image", nargs="?", default="金酱.png", help="图片文件路径")
    parser.add_argument("--preview", action="store_true", help="生成区域预览图")
    parser.add_argument("--info", action="store_true", help="显示区域信息")

    args = parser.parse_args()

    try:
        # 初始化修改器
        modifier = BottleModifier(args.image)

        if args.preview:
            modifier.preview_regions()
            return

        if args.info:
            modifier.show_regions_info()
            return

        # 交互式修改
        interactive_mode(modifier)

    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        print("💡 请确保图片文件存在")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


def interactive_mode(modifier):
    """交互式模式"""
    print("\n🎨 金酱酒瓶文字定制工具")
    print("=" * 40)

    modifier.show_regions_info()

    while True:
        print("\n📋 操作选项:")
        print("1. 添加单个文字")
        print("2. 批量添加文字")
        print("3. 预设方案")
        print("4. 保存图片")
        print("5. 重置图片")
        print("6. 生成区域预览")
        print("0. 退出")

        choice = input("\n请选择操作 (0-6): ").strip()

        if choice == "0":
            print("👋 再见!")
            break
        elif choice == "1":
            add_single_text(modifier)
        elif choice == "2":
            add_batch_texts(modifier)
        elif choice == "3":
            apply_preset(modifier)
        elif choice == "4":
            save_image(modifier)
        elif choice == "5":
            modifier.reset_image()
        elif choice == "6":
            modifier.preview_regions()
        else:
            print("❌ 无效选择，请重新输入")


def add_single_text(modifier):
    """添加单个文字"""
    try:
        region_id = int(input("请输入区域ID (1-4): "))
        text = input("请输入文字内容: ").strip()

        if not text:
            print("❌ 文字内容不能为空")
            return

        # 可选样式设置
        font_size = input("字体大小 (默认12): ").strip()
        font_color = input("字体颜色 (默认#000000): ").strip()

        style_options = {}
        if font_size:
            style_options["font_size"] = int(font_size)
        if font_color:
            style_options["font_color"] = font_color

        modifier.add_text_to_region(text, region_id, **style_options)

    except ValueError:
        print("❌ 输入格式错误")
    except Exception as e:
        print(f"❌ 操作失败: {e}")


def add_batch_texts(modifier):
    """批量添加文字"""
    print("\n批量添加模式 - 为4个区域分别输入文字")
    text_configs = []

    for i in range(1, 5):
        region = modifier.get_region(i)
        text = input(f"区域{i} ({region['name']}) 的文字 (回车跳过): ").strip()

        if text:
            text_configs.append({
                "region_id": i,
                "text": text,
                "font_size": 12,
                "font_color": "#000000"
            })

    if text_configs:
        modifier.batch_add_texts(text_configs)
    else:
        print("❌ 没有输入任何文字")


def apply_preset(modifier):
    """应用预设方案"""
    presets = {
        "1": {
            "name": "金酱经典",
            "configs": [
                {"region_id": 1, "text": "金", "font_color": "#FFD700", "font_size": 14},
                {"region_id": 2, "text": "酱", "font_color": "#FFD700", "font_size": 14},
                {"region_id": 3, "text": "香", "font_color": "#8B4513", "font_size": 12},
                {"region_id": 4, "text": "醇", "font_color": "#8B4513", "font_size": 12}
            ]
        },
        "2": {
            "name": "典雅黑金",
            "configs": [
                {"region_id": 1, "text": "典", "font_color": "#000000", "font_size": 13},
                {"region_id": 2, "text": "雅", "font_color": "#000000", "font_size": 13},
                {"region_id": 3, "text": "珍", "font_color": "#FFD700", "font_size": 12},
                {"region_id": 4, "text": "品", "font_color": "#FFD700", "font_size": 12}
            ]
        },
        "3": {
            "name": "自定义四字",
            "configs": None  # 需要用户输入
        }
    }

    print("\n🎨 预设方案:")
    for key, preset in presets.items():
        print(f"{key}. {preset['name']}")

    choice = input("\n请选择预设方案 (1-3): ").strip()

    if choice in presets:
        preset = presets[choice]

        if preset["configs"]:
            print(f"\n应用预设: {preset['name']}")
            modifier.batch_add_texts(preset["configs"])
        else:
            # 自定义四字
            print("\n请输入四个字:")
            chars = []
            for i in range(4):
                char = input(f"第{i + 1}个字: ").strip()
                if char:
                    chars.append(char)

            if len(chars) == 4:
                configs = [
                    {"region_id": i + 1, "text": char, "font_size": 13, "font_color": "#000000"}
                    for i, char in enumerate(chars)
                ]
                modifier.batch_add_texts(configs)
            else:
                print("❌ 需要输入完整的4个字")
    else:
        print("❌ 无效选择")


def save_image(modifier):
    """保存图片"""
    filename = input("输入文件名 (回车使用默认名称): ").strip()

    if filename:
        if not filename.endswith(('.png', '.jpg', '.jpeg')):
            filename += '.png'
        output_path = modifier.output_dir / filename
    else:
        output_path = None

    result_path = modifier.save_result(output_path)
    if result_path:
        print(f"✅ 图片保存成功!")


if __name__ == "__main__":
    # 直接运行交互模式的示例
    if len(sys.argv) == 1:
        try:
            modifier = BottleModifier("金酱.png")
            interactive_mode(modifier)
        except FileNotFoundError:
            print("❌ 找不到 '金酱.png' 文件")
            print("💡 请将脚本和图片文件放在同一目录下")
        except Exception as e:
            print(f"❌ 错误: {e}")
    else:
        main()
