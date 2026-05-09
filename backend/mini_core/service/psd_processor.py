import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from flask import current_app
from loguru import logger
from PIL import Image, ImageDraw, ImageFont
from psd_tools import PSDImage
from werkzeug.utils import secure_filename


@dataclass
class TextAttributes:
    text: str
    font_name: str
    font_size: int
    color: Tuple[int, int, int, int]
    position: Tuple[int, int]
    transform: Any
    layer_size: Tuple[int, int]


class FontManager:
    FALLBACK_FONTS = [
        '庞中华毛笔隶书简体.ttf',
        'simkai.ttf',
        'simhei.ttf',
        'simsun.ttc',
        'msyh.ttc',
        'simfang.ttf',
        'STKAITI.TTF',
        'STXIHEI.TTF',
        'STZHONGS.TTF',
        'STFANGSO.TTF',
    ]

    @staticmethod
    def load_font(font_name: str, font_size: int) -> ImageFont.FreeTypeFont:
        try:
            font_bases = [
                str(font_name).replace("'", "").lower(),
                str(font_name).replace("'", ""),
                str(font_name).replace("'", "").replace("-", ""),
                str(font_name).replace("'", "").replace("-Regular", ""),
            ]
            extensions = ['.ttf', '.ttc', '.TTF', '.TTC', '.otf']

            for base in font_bases:
                for ext in extensions:
                    try:
                        return ImageFont.truetype(base + ext, font_size)
                    except Exception:
                        continue

            logger.warning("PSD 字体加载失败，尝试备用字体 font_name={}", font_name)
            for fallback_font in FontManager.FALLBACK_FONTS:
                try:
                    return ImageFont.truetype(fallback_font, font_size)
                except Exception as exc:
                    logger.debug("备用字体不可用 fallback_font={} error={}", fallback_font, exc)

            logger.warning("所有字体加载失败，使用 PIL 默认字体 font_name={}", font_name)
            return ImageFont.load_default()
        except Exception as exc:
            logger.exception("字体加载过程异常 font_name={} font_size={} error={}", font_name, font_size, exc)
            return ImageFont.load_default()


def build_repeated_text(new_text: str) -> str:
    if len(new_text) >= 2:
        first_char = new_text[0] * 2
        second_char = new_text[1] * 2
        return second_char + first_char + second_char + first_char
    return new_text


def process_psd_file(psd_path: str, new_text: str) -> Dict[str, Any]:
    new_text = build_repeated_text(new_text)

    if not Path(psd_path).exists():
        return {
            "code": 400,
            "message": f"PSD文件不存在: {psd_path}",
            "data": None,
        }

    try:
        with tempfile.TemporaryDirectory(prefix='psd_processor_') as temp_dir:
            temp_path = Path(temp_dir)
            psd = PSDImage.open(psd_path)
            output_image = render_psd_with_text(psd, new_text, temp_path)
            filename = save_file(output_image)
            file_url = get_file_url(filename)
            return {
                "code": 200,
                "message": "处理完成! ",
                "data": {"url": file_url},
            }
    except Exception as exc:
        logger.exception("PSD 处理失败 psd_path={} new_text={} error={}", psd_path, new_text, exc)
        return {
            "code": 500,
            "message": f"PSD处理失败: {str(exc)}",
            "data": None,
        }


def render_psd_with_text(psd, new_text: str, temp_path: Path) -> Image.Image:
    layer_index = 0
    layers_to_remove = []
    file_name_color = [
        {'file_name': temp_path / f'bg{index}.png', 'color': color}
        for index, color in enumerate([
            (255, 0, 0, 0),
            (0, 255, 0, 0),
            (0, 0, 255, 0),
            (255, 255, 255, 0),
            (255, 0, 0, 0),
            (0, 255, 0, 0),
            (0, 0, 255, 0),
            (255, 255, 255, 0),
        ])
    ]

    for index, layer in enumerate(psd):
        if layer.is_group():
            for sublayer in layer:
                if sublayer.kind == 'type':
                    if layer_index >= len(new_text):
                        logger.warning(
                            "PSD 文本图层数量超过可替换文本长度 layer_index={} text_length={} layer_name={}",
                            layer_index,
                            len(new_text),
                            getattr(sublayer, 'name', None),
                        )
                        continue
                    create_text_image_with_psd_attributes(
                        psd,
                        sublayer,
                        new_text[layer_index],
                        layer_index,
                        file_name_color,
                        temp_path,
                    )
                    layer_index += 1
                else:
                    logger.debug(
                        "跳过非文本子图层 index={} layer_kind={} layer_name={}",
                        index,
                        getattr(sublayer, 'kind', None),
                        getattr(sublayer, 'name', None),
                    )
            layers_to_remove.append(layer)
        else:
            logger.debug(
                "跳过非组图层 index={} layer_kind={} layer_name={}",
                index,
                getattr(layer, 'kind', None),
                getattr(layer, 'name', None),
            )

    for layer in layers_to_remove:
        logger.debug("清理被替换图层 layer_kind={} layer_name={}", getattr(layer, 'kind', None), getattr(layer, 'name', None))
        layer.clear()

    background_path = temp_path / 'background.png'
    psd.composite().save(background_path)
    background = Image.open(background_path)

    for item in file_name_color:
        if not item['file_name'].exists():
            continue
        image_obj = Image.open(item['file_name'])
        color_layer = Image.new('RGBA', background.size, item['color'])
        background = Image.composite(color_layer, background, image_obj)

    return background


def convert_psd_text_to_imagedraw(layer) -> Optional[Dict[str, Any]]:
    try:
        text = layer.engine_dict['Editor']['Text'].value
        fontset = layer.resource_dict['FontSet']
        rundata = layer.engine_dict['StyleRun']['RunArray']
        font_info = parse_font_info(fontset)
        color_info = parse_color_info(rundata)
        font_size = parse_font_size(rundata)
        transform = layer.transform
        position = (layer.left, layer.top)

        return {
            'text': text,
            'font_name': font_info['font_name'],
            'font_size': font_size,
            'color': color_info,
            'position': position,
            'transform': transform,
            'layer_size': layer.size,
        }
    except Exception as exc:
        logger.exception("转换 PSD 文本图层属性失败 layer_name={} error={}", getattr(layer, 'name', None), exc)
        return None


def parse_font_info(fontset):
    try:
        if fontset and len(fontset) > 0:
            for font in fontset:
                if font['Name'] != 'AdobeInvisFont':
                    return {
                        'font_name': font['Name'],
                        'script': font.get('Script', 0),
                        'font_type': font.get('FontType', 0),
                    }
            return {
                'font_name': fontset[0]['Name'],
                'script': fontset[0].get('Script', 0),
                'font_type': fontset[0].get('FontType', 0),
            }
    except Exception as exc:
        logger.exception("解析 PSD 字体信息失败 error={}", exc)

    return {'font_name': 'Arial', 'script': 0, 'font_type': 0}


def parse_color_info(rundata):
    try:
        style_data = None
        if rundata and len(rundata) > 1:
            style_data = rundata[1]['StyleSheet']['StyleSheetData']
        elif rundata and len(rundata) > 0:
            style_data = rundata[0]['StyleSheet']['StyleSheetData']

        if style_data and 'FillColor' in style_data:
            fill_color = style_data['FillColor']
            if fill_color['Type'] == 1:
                values = fill_color['Values']
                a = int(values[0] * 255)
                r = int(values[1] * 255)
                g = int(values[2] * 255)
                b = int(values[3] * 255)
                return (r, g, b, a)
    except Exception as exc:
        logger.exception("解析 PSD 文本颜色失败 error={}", exc)

    return (0, 0, 0, 255)


def parse_font_size(rundata):
    try:
        style_data = None
        if rundata and len(rundata) > 1:
            style_data = rundata[1]['StyleSheet']['StyleSheetData']
        elif rundata and len(rundata) > 0:
            style_data = rundata[0]['StyleSheet']['StyleSheetData']

        if style_data and 'FontSize' in style_data:
            return int(style_data['FontSize'])
    except Exception as exc:
        logger.exception("解析 PSD 文本字号失败 error={}", exc)

    return 20


def create_text_image_with_psd_attributes(psd, layer, new_text, index, file_name_color, temp_path: Path):
    try:
        text_attrs = convert_psd_text_to_imagedraw(layer)
        if not text_attrs:
            logger.warning("无法获取文本图层属性 layer_name={}", getattr(layer, 'name', None))
            return None

        logger.debug(
            "替换 PSD 文本 layer_name={} old_text={} new_text={} font={} font_size={} color={} position={}",
            getattr(layer, 'name', None),
            text_attrs['text'],
            new_text,
            text_attrs['font_name'],
            text_attrs['font_size'],
            text_attrs['color'],
            text_attrs['position'],
        )

        img = Image.new('RGBA', layer.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = FontManager.load_font(text_attrs['font_name'], text_attrs['font_size'])
        text_bbox = draw.textbbox((0, 0), new_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x = (layer.size[0] - text_width) // 2
        draw.text((x, -35), new_text, font=font, fill=text_attrs['color'])

        tmp_file = temp_path / f'tmp{index}.png'
        img.save(tmp_file)
        bg = Image.new('RGBA', psd.size, (0, 0, 0, 0))
        file1 = Image.open(tmp_file)
        bg.paste(file1, (text_attrs['position'][0], text_attrs['position'][1]))
        bg.save(file_name_color[index]['file_name'])
        file_name_color[index]['color'] = text_attrs['color']
        return file_name_color[index]
    except Exception as exc:
        logger.exception(
            "创建 PSD 替换文本图像失败 layer_name={} index={} new_text={} error={}",
            getattr(layer, 'name', None),
            index,
            new_text,
            exc,
        )
        return None


def save_file(file) -> str:
    original_name = Path(getattr(file, 'filename', 'finish.png')).name
    original_filename = secure_filename(original_name)
    extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    timestamp = datetime.now().strftime('%Y%m%d')
    unique_filename = f"{timestamp}_{uuid.uuid4().hex}.{extension}" if extension else f"{timestamp}_{uuid.uuid4().hex}"

    image_path = current_app.config.get('IMAGE_PATH')
    upload_dir = Path(image_path)
    date_dir = upload_dir / timestamp
    if not date_dir.exists():
        date_dir.mkdir(parents=True, exist_ok=True)

    file_path = date_dir / unique_filename
    file.save(file_path)
    return f"{str(Path(timestamp))}/{unique_filename}"


def get_file_url(filename: str) -> str:
    base_url = current_app.config.get('UPLOADS_URL_PREFIX', '/files')
    return f"{base_url}{filename}"
