#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确适配浮雕生成器 - 字体大小精确适配区域
确保文字不超出指定区域范围
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path


class FittedEmbossGenerator:
    """精确适配浮雕生成器"""

    def __init__(self):
        self.regions = [
            {"id": 1, "x": 201, "y": 187, "width": 26, "height": 27, "name": "上部标签"},
            {"id": 2, "x": 202, "y": 240, "width": 27, "height": 26, "name": "下部标签"},
            {"id": 3, "x": 313, "y": 118, "width": 25, "height": 27, "name": "右上区域"},
            {"id": 4, "x": 315, "y": 177, "width": 27, "height": 24, "name": "右下区域"}
        ]

        # 字体配置
        self.fonts = {
            "楷书": "fonts/AaBiMoHengZiZhenBaoKaiShu-2.ttf",
            "宋体": "fonts/ShanHaiJiGuJiangNanSongKeW-2.ttf"
        }

        Path("output").mkdir(exist_ok=True)
        self.check_fonts()

    def check_fonts(self):
        """检查字体文件"""
        print("🔍 检查字体文件...")
        for font_name, font_path in self.fonts.items():
            if os.path.exists(font_path):
                print(f"✅ {font_name}: {font_path}")
            else:
                print(f"❌ {font_name}: {font_path} (文件不存在)")
        print()

    def load_font(self, font_type, font_size):
        """加载字体"""
        font_path = self.fonts.get(font_type)
        if font_path and os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, font_size)
            except:
                pass
        return ImageFont.load_default()

    def find_optimal_font_size(self, text, width, height, font_type, max_attempts=20):
        """
        找到最佳字体大小，确保文字完全适配区域

        Args:
            text: 文字内容
            width: 区域宽度
            height: 区域高度
            font_type: 字体类型
            max_attempts: 最大尝试次数

        Returns:
            最佳字体大小和字体对象
        """
        # 保守的起始字体大小
        start_size = min(width, height) - 6  # 留6像素边距
        start_size = max(start_size, 8)  # 最小8像素

        optimal_size = start_size
        optimal_font = None

        # 从起始大小开始向上尝试
        for attempt in range(max_attempts):
            test_size = start_size + attempt
            if test_size > min(width, height):  # 不能超过区域最小尺寸
                break

            font = self.load_font(font_type, test_size)

            # 创建临时绘制对象测试文字尺寸
            temp_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)

            bbox = temp_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 检查是否适配（留2像素边距）
            if text_width <= width - 4 and text_height <= height - 4:
                optimal_size = test_size
                optimal_font = font
            else:
                break  # 超出范围，停止尝试

        if optimal_font is None:
            optimal_font = self.load_font(font_type, optimal_size)

        print(f"🎯 文字 '{text}' 区域{width}x{height} -> 最佳字体大小: {optimal_size}px")
        return optimal_size, optimal_font

    def create_fitted_emboss_text(self, text, width, height, font_type="楷书"):
        """
        创建精确适配的浮雕文字

        Args:
            text: 文字内容
            width: 宽度
            height: 高度
            font_type: 字体类型

        Returns:
            PIL Image对象
        """
        # 找到最佳字体大小
        font_size, font = self.find_optimal_font_size(text, width, height, font_type)

        # 创建透明画布
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 计算文字位置 - 精确居中
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # 确保文字不会超出边界
        x = max(1, min(x, width - text_width - 1))
        y = max(1, min(y, height - text_height - 1))

        # 创建适度的浮雕效果

        # 阴影层 - 根据区域大小调整偏移
        shadow_offset = max(1, min(width, height) // 20)  # 动态偏移
        shadow_x = min(width - 1, x + shadow_offset)
        shadow_y = min(height - 1, y + shadow_offset)
        draw.text((shadow_x, shadow_y), text, font=font, fill=(60, 60, 60, 160))

        # 高光层
        highlight_offset = max(1, shadow_offset)
        highlight_x = max(0, x - highlight_offset)
        highlight_y = max(0, y - highlight_offset)
        draw.text((highlight_x, highlight_y), text, font=font, fill=(255, 255, 255, 120))

        # 主文字层 - 纯黑色
        draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))

        return img

    def create_enhanced_fitted_emboss(self, text, width, height, font_type="楷书"):
        """
        创建增强版精确适配浮雕文字

        Args:
            text: 文字内容
            width: 宽度
            height: 高度
            font_type: 字体类型

        Returns:
            PIL Image对象
        """
        # 找到最佳字体大小
        font_size, font = self.find_optimal_font_size(text, width, height, font_type)

        # 创建透明画布
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 计算文字位置
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # 确保不超出边界
        x = max(2, min(x, width - text_width - 2))
        y = max(2, min(y, height - text_height - 2))

        # 增强版浮雕效果 - 多层但控制在区域内

        # 计算安全偏移量
        max_offset = min(3, min(width, height) // 10)

        # 深阴影层
        if x + max_offset < width and y + max_offset < height:
            draw.text((x + max_offset, y + max_offset), text, font=font, fill=(30, 30, 30, 140))

        # 中阴影层
        mid_offset = max(1, max_offset - 1)
        if x + mid_offset < width and y + mid_offset < height:
            draw.text((x + mid_offset, y + mid_offset), text, font=font, fill=(60, 60, 60, 160))

        # 高光层
        if x >= max_offset and y >= max_offset:
            draw.text((x - max_offset, y - max_offset), text, font=font, fill=(255, 255, 255, 100))

        if x >= mid_offset and y >= mid_offset:
            draw.text((x - mid_offset, y - mid_offset), text, font=font, fill=(255, 255, 255, 120))

        # 主文字层 - 纯黑色
        draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))

        return img

    def generate_fitted_samples(self):
        """生成精确适配样本"""
        print("📋 生成精确适配样本...")

        # 测试不同尺寸
        test_sizes = [
            (20, 20, "超小"),
            (26, 27, "小型"),
            (40, 40, "中型"),
            (60, 60, "大型")
        ]

        test_chars = ["金", "酱", "典", "藏"]

        for char in test_chars:
            for width, height, size_name in test_sizes:
                # 标准适配版
                fitted_img = self.create_fitted_emboss_text(char, width, height, "楷书")
                fitted_path = f"output/{char}_{size_name}_{width}x{height}_适配版.png"
                fitted_img.save(fitted_path)
                print(f"✅ 适配版: {fitted_path}")

                # 增强适配版
                enhanced_img = self.create_enhanced_fitted_emboss(char, width, height, "楷书")
                enhanced_path = f"output/{char}_{size_name}_{width}x{height}_增强适配版.png"
                enhanced_img.save(enhanced_path)
                print(f"✅ 增强版: {enhanced_path}")

    def apply_fitted_to_bottle(self, text_configs, font_type="楷书", enhanced=False):
        """应用精确适配文字到酒瓶"""
        effect_type = "增强版" if enhanced else "标准版"
        print(f"🍶 生成{effect_type}精确适配酒瓶...")

        try:
            bottle = Image.open("金酱.png").convert('RGBA')
            print("✅ 成功加载酒瓶图片")
        except:
            print("❌ 找不到金酱.png文件")
            return None

        for config in text_configs:
            region_id = config["region_id"]
            text = config["text"]

            region = next((r for r in self.regions if r["id"] == region_id), None)
            if not region:
                print(f"⚠️ 跳过未知区域: {region_id}")
                continue

            # 创建精确适配的浮雕文字
            if enhanced:
                emboss_text = self.create_enhanced_fitted_emboss(
                    text, region["width"], region["height"], font_type
                )
            else:
                emboss_text = self.create_fitted_emboss_text(
                    text, region["width"], region["height"], font_type
                )

            # 叠加到酒瓶 - 精确位置
            bottle.paste(emboss_text, (region["x"], region["y"]), emboss_text)
            print(f"✅ 已添加适配文字 '{text}' 到{region['name']}")

        return bottle


def main():
    """主函数"""
    print("🎯 精确适配浮雕生成器")
    print("=" * 40)
    print("✨ 特点: 字体大小精确适配区域，绝不超出范围")
    print()

    generator = FittedEmbossGenerator()

    # 1. 生成不同尺寸的适配样本
    print("1️⃣ 生成精确适配样本...")
    generator.generate_fitted_samples()

    # 2. 生成标准版精确适配酒瓶
    print("\n2️⃣ 生成标准版精确适配酒瓶...")
    standard_configs = [
        {"region_id": 1, "text": "金"},
        {"region_id": 2, "text": "酱"},
        {"region_id": 3, "text": "香"},
        {"region_id": 4, "text": "醇"}
    ]

    bottle_standard = generator.apply_fitted_to_bottle(standard_configs, "楷书", enhanced=False)
    if bottle_standard:
        bottle_standard.save("output/精确适配酒瓶_标准版.png")
        print("💾 已保存: 精确适配酒瓶_标准版.png")

    # 3. 生成增强版精确适配酒瓶
    print("\n3️⃣ 生成增强版精确适配酒瓶...")
    enhanced_configs = [
        {"region_id": 1, "text": "典"},
        {"region_id": 2, "text": "藏"},
        {"region_id": 3, "text": "珍"},
        {"region_id": 4, "text": "品"}
    ]

    bottle_enhanced = generator.apply_fitted_to_bottle(enhanced_configs, "楷书", enhanced=True)
    if bottle_enhanced:
        bottle_enhanced.save("output/精确适配酒瓶_增强版.png")
        print("💾 已保存: 精确适配酒瓶_增强版.png")

    # 4. 生成宋体版本
    print("\n4️⃣ 生成宋体精确适配酒瓶...")
    songti_configs = [
        {"region_id": 1, "text": "福"},
        {"region_id": 2, "text": "禄"},
        {"region_id": 3, "text": "寿"},
        {"region_id": 4, "text": "喜"}
    ]

    bottle_songti = generator.apply_fitted_to_bottle(songti_configs, "宋体", enhanced=True)
    if bottle_songti:
        bottle_songti.save("output/宋体精确适配酒瓶.png")
        print("💾 已保存: 宋体精确适配酒瓶.png")

    print("\n🎉 精确适配浮雕生成完成！")
    print("📁 请查看 output 文件夹中的结果")
    print("\n📋 核心改进:")
    print("   🎯 精确适配 - 字体大小自动适配区域")
    print("   📏 边界控制 - 绝不超出指定范围")
    print("   🔍 智能计算 - 找到最佳字体大小")
    print("   ✨ 适度浮雕 - 效果和尺寸平衡")
    print("   ⚫ 纯黑文字 + 透明背景")
    print("   🎨 多种效果 - 标准版和增强版")
    print("\n💡 区域尺寸:")
    for region in generator.regions:
        print(f"   区域{region['id']}: {region['width']}x{region['height']}px - {region['name']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        import traceback

        traceback.print_exc()
