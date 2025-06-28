#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清晰浮雕文字生成器 - 解决楷体模糊问题
使用更清晰的字体 + 优化的浮雕效果
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path


class ClearEmbossGenerator:
    """清晰浮雕文字生成器"""

    def __init__(self):
        self.regions = [
            {"id": 1, "x": 201, "y": 187, "width": 26, "height": 27, "name": "上部标签"},
            {"id": 2, "x": 202, "y": 240, "width": 27, "height": 26, "name": "下部标签"},
            {"id": 3, "x": 313, "y": 118, "width": 25, "height": 27, "name": "右上区域"},
            {"id": 4, "x": 315, "y": 177, "width": 27, "height": 24, "name": "右下区域"}
        ]

        Path("output").mkdir(exist_ok=True)

    def get_clear_font(self, font_size):
        """获取清晰字体 - 优先黑体和粗体"""
        font_paths = [
            # Windows 清晰字体 (优先粗体)
            "C:/Windows/Fonts/simhei.ttf",  # 黑体 (最清晰)
            "C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑 Bold
            "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
            "C:/Windows/Fonts/STZHONGS.TTF",  # 华文中宋 (比楷体清晰)
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
            # macOS 清晰字体
            "/System/Library/Fonts/PingFang.ttc",  # 苹方 (很清晰)
            "/Library/Fonts/Arial Unicode.ttf",  # Arial Unicode
            "/System/Library/Fonts/Helvetica.ttc",  # Helvetica
            # Linux 字体
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except:
                    continue

        return ImageFont.load_default()

    def create_sharp_emboss_text(self, text, width, height, font_size=20):
        """
        创建清晰的浮雕文字效果

        Args:
            text: 文字内容
            width: 宽度
            height: 高度
            font_size: 字体大小

        Returns:
            PIL Image对象 (透明背景)
        """
        # 自动调整字体大小
        max_font_size = min(width, height) - 2
        if font_size > max_font_size:
            font_size = max_font_size

        # 创建透明画布
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 获取清晰字体
        font = self.get_clear_font(font_size)

        # 计算文字位置
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # 创建清晰的浮雕效果

        # 深阴影层 (右下)
        draw.text((x + 2, y + 2), text, font=font, fill=(40, 40, 40, 200))

        # 中阴影层
        draw.text((x + 1, y + 1), text, font=font, fill=(80, 80, 80, 180))

        # 高光层 (左上)
        draw.text((x - 1, y - 1), text, font=font, fill=(255, 255, 255, 120))

        # 主文字层 - 纯黑色
        draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))

        return img

    def create_bold_emboss_text(self, text, width, height, font_size=20):
        """
        创建加粗版清晰浮雕文字

        Args:
            text: 文字内容
            width: 宽度
            height: 高度
            font_size: 字体大小

        Returns:
            PIL Image对象 (透明背景)
        """
        # 调整字体大小
        max_font_size = min(width, height) - 2
        if font_size > max_font_size:
            font_size = max_font_size

        # 创建透明画布
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 获取字体
        font = self.get_clear_font(font_size)

        # 计算文字位置
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # 加粗效果 - 多次绘制增加厚度
        bold_positions = [
            (x, y),  # 主位置
            (x + 1, y),  # 右偏移
            (x, y + 1),  # 下偏移
            (x + 1, y + 1),  # 右下偏移
        ]

        # 深阴影层
        for dx in range(3):
            for dy in range(3):
                shadow_x = x + 2 + dx
                shadow_y = y + 2 + dy
                if shadow_x < width and shadow_y < height:
                    alpha = 150 - (dx + dy) * 20  # 渐变透明度
                    draw.text((shadow_x, shadow_y), text, font=font, fill=(30, 30, 30, max(alpha, 50)))

        # 中阴影层
        for pos in [(x + 1, y + 1), (x + 2, y + 1), (x + 1, y + 2)]:
            draw.text(pos, text, font=font, fill=(60, 60, 60, 180))

        # 高光层
        for pos in [(x - 1, y - 1), (x - 2, y - 1), (x - 1, y - 2)]:
            if pos[0] >= 0 and pos[1] >= 0:
                draw.text(pos, text, font=font, fill=(255, 255, 255, 100))

        # 主文字层 - 加粗绘制
        for pos in bold_positions:
            draw.text(pos, text, font=font, fill=(0, 0, 0, 255))

        return img

    def create_premium_emboss_text(self, text, width, height, font_size=20):
        """
        创建高级清晰浮雕文字 (最佳效果)

        Args:
            text: 文字内容
            width: 宽度
            height: 高度
            font_size: 字体大小

        Returns:
            PIL Image对象 (透明背景)
        """
        # 调整字体大小
        max_font_size = min(width, height) - 2
        if font_size > max_font_size:
            font_size = max_font_size

        # 创建透明画布
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 获取字体
        font = self.get_clear_font(font_size)

        # 计算文字位置
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # 高级浮雕效果

        # 第一层：远距离深阴影
        draw.text((x + 3, y + 3), text, font=font, fill=(20, 20, 20, 120))

        # 第二层：中距离阴影
        draw.text((x + 2, y + 2), text, font=font, fill=(50, 50, 50, 160))

        # 第三层：近距离阴影
        draw.text((x + 1, y + 1), text, font=font, fill=(100, 100, 100, 140))

        # 第四层：远距离高光
        if x >= 2 and y >= 2:
            draw.text((x - 2, y - 2), text, font=font, fill=(255, 255, 255, 60))

        # 第五层：近距离高光
        if x >= 1 and y >= 1:
            draw.text((x - 1, y - 1), text, font=font, fill=(255, 255, 255, 100))

        # 第六层：加粗主文字
        main_positions = [
            (x, y),
            (x + 0.5, y),  # 微调位置增加清晰度
            (x, y + 0.5),
        ]

        for pos in main_positions:
            px, py = int(pos[0]), int(pos[1])
            draw.text((px, py), text, font=font, fill=(0, 0, 0, 255))

        return img

    def generate_sample_texts(self):
        """生成清晰浮雕样本"""
        print("📋 生成清晰浮雕文字样本...")

        samples = [
            {"text": "金", "name": "金字_清晰版"},
            {"text": "酱", "name": "酱字_清晰版"},
            {"text": "典", "name": "典字_清晰版"},
            {"text": "藏", "name": "藏字_清晰版"}
        ]

        for sample in samples:
            # 标准清晰版
            sharp_img = self.create_sharp_emboss_text(
                sample["text"],
                100, 100,
                40
            )
            sharp_path = f"output/{sample['name']}_标准.png"
            sharp_img.save(sharp_path)
            print(f"✅ 已生成: {sharp_path}")

            # 加粗清晰版
            bold_img = self.create_bold_emboss_text(
                sample["text"],
                100, 100,
                40
            )
            bold_path = f"output/{sample['name']}_加粗.png"
            bold_img.save(bold_path)
            print(f"✅ 已生成: {bold_path}")

            # 高级清晰版
            premium_img = self.create_premium_emboss_text(
                sample["text"],
                100, 100,
                40
            )
            premium_path = f"output/{sample['name']}_高级.png"
            premium_img.save(premium_path)
            print(f"✅ 已生成: {premium_path}")

    def apply_to_bottle(self, text_configs, effect_type="premium"):
        """
        应用到酒瓶图片

        Args:
            text_configs: 配置列表
            effect_type: 效果类型 ("sharp", "bold", "premium")
        """
        effect_names = {"sharp": "标准清晰", "bold": "加粗", "premium": "高级"}
        print(f"🍶 开始生成{effect_names[effect_type]}浮雕酒瓶...")

        try:
            bottle = Image.open("金酱.png").convert('RGBA')
            print("✅ 成功加载酒瓶图片")
        except:
            print("❌ 找不到金酱.png文件")
            return None

        for config in text_configs:
            region_id = config["region_id"]
            text = config["text"]
            font_size = config.get("font_size", 20)

            # 找到对应区域
            region = None
            for r in self.regions:
                if r["id"] == region_id:
                    region = r
                    break

            if not region:
                print(f"⚠️ 跳过未知区域: {region_id}")
                continue

            # 创建对应效果的文字
            if effect_type == "sharp":
                emboss_text = self.create_sharp_emboss_text(
                    text, region["width"], region["height"], font_size
                )
            elif effect_type == "bold":
                emboss_text = self.create_bold_emboss_text(
                    text, region["width"], region["height"], font_size
                )
            else:  # premium
                emboss_text = self.create_premium_emboss_text(
                    text, region["width"], region["height"], font_size
                )

            # 叠加到酒瓶
            bottle.paste(emboss_text, (region["x"], region["y"]), emboss_text)
            print(f"✅ 已添加清晰文字 '{text}' 到{region['name']}")

        return bottle


def main():
    """主函数"""
    print("🔍 清晰浮雕文字生成器")
    print("=" * 30)
    print("💡 解决楷体模糊问题，使用更清晰的字体")
    print("📝 特点: 黑体/粗体 + 清晰效果 + 透明背景")
    print()

    generator = ClearEmbossGenerator()

    # 1. 生成样本对比
    generator.generate_sample_texts()

    # 2. 生成标准清晰版酒瓶
    print("\n🔍 生成标准清晰版酒瓶...")
    sharp_configs = [
        {"region_id": 1, "text": "金", "font_size": 22},
        {"region_id": 2, "text": "酱", "font_size": 22},
        {"region_id": 3, "text": "香", "font_size": 20},
        {"region_id": 4, "text": "醇", "font_size": 20}
    ]

    bottle_sharp = generator.apply_to_bottle(sharp_configs, "sharp")
    if bottle_sharp:
        bottle_sharp.save("output/清晰浮雕酒瓶_标准版.png")
        print("💾 已保存: 清晰浮雕酒瓶_标准版.png")

    # 3. 生成加粗清晰版酒瓶
    print("\n💪 生成加粗清晰版酒瓶...")
    bold_configs = [
        {"region_id": 1, "text": "典", "font_size": 22},
        {"region_id": 2, "text": "藏", "font_size": 22},
        {"region_id": 3, "text": "珍", "font_size": 20},
        {"region_id": 4, "text": "品", "font_size": 20}
    ]

    bottle_bold = generator.apply_to_bottle(bold_configs, "bold")
    if bottle_bold:
        bottle_bold.save("output/清晰浮雕酒瓶_加粗版.png")
        print("💾 已保存: 清晰浮雕酒瓶_加粗版.png")

    # 4. 生成高级清晰版酒瓶 (推荐)
    print("\n⭐ 生成高级清晰版酒瓶 (推荐)...")
    premium_configs = [
        {"region_id": 1, "text": "福", "font_size": 24},
        {"region_id": 2, "text": "禄", "font_size": 24},
        {"region_id": 3, "text": "寿", "font_size": 22},
        {"region_id": 4, "text": "喜", "font_size": 22}
    ]

    bottle_premium = generator.apply_to_bottle(premium_configs, "premium")
    if bottle_premium:
        bottle_premium.save("output/清晰浮雕酒瓶_高级版.png")
        print("💾 已保存: 清晰浮雕酒瓶_高级版.png")

    print("\n🎉 清晰浮雕效果生成完成！")
    print("📁 请查看 output 文件夹中的文件")
    print("\n📋 生成的文件包括:")
    print("   - 各种样本文字 (标准/加粗/高级 三个版本)")
    print("   - 清晰浮雕酒瓶_标准版.png")
    print("   - 清晰浮雕酒瓶_加粗版.png")
    print("   - 清晰浮雕酒瓶_高级版.png (推荐)")
    print("\n🔍 改进特点:")
    print("   📝 使用黑体/粗体替代楷体")
    print("   ⚡ 优化渲染，避免模糊")
    print("   ⚫ 纯黑色文字")
    print("   🔍 透明背景")
    print("   💪 多种厚度选择")
    print("   ✨ 清晰的浮雕效果")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 生成过程中出现错误: {e}")
        print("💡 请确保金酱.png文件在当前目录下")
