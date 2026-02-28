import openai
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap
import os

class ContentEngine:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    def overlay_text(self, image_url, title, account_name, font_name):
        """Накладывает текст с выбранным шрифтом"""
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        
        txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # Словарь путей к шрифтам
        font_paths = {
            "Montserrat": "fonts/Montserrat-Bold.ttf",
            "Bebas Neue": "fonts/BebasNeue-Regular.ttf",
            "Inter": "fonts/Inter-Black.ttf",
            "Oswald": "fonts/Oswald-Medium.ttf"
        }
        
        target_font_path = font_paths.get(font_name, "arial.ttf")
        
        # Если файла нет, Pillow выдаст ошибку, поэтому делаем проверку
        if not os.path.exists(target_font_path):
            font_title = ImageFont.load_default()
            font_acc = ImageFont.load_default()
        else:
            font_title = ImageFont.truetype(target_font_path, 75) # Заголовок крупнее
            font_acc = ImageFont.truetype(target_font_path, 35)   # Аккаунт мельче

        width, height = img.size

        # 1. ЗАГОЛОВОК (Сверху)
        # Автоматический перенос строк, если текст длинный
        lines = textwrap.wrap(title.upper(), width=18) 
        current_h = 80
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_title)
            w = bbox[2] - bbox[0]
            # Тень для читаемости
            draw.text(((width - w) / 2 + 3, current_h + 3), line, font=font_title, fill=(0, 0, 0, 180))
            # Основной текст
            draw.text(((width - w) / 2, current_h), line, font=font_title, fill="white")
            current_h += 90

        # 2. АККАУНТ (Снизу справа)
        acc_text = f"@{account_name.replace('@', '')}"
        bbox_acc = draw.textbbox((0, 0), acc_text, font=font_acc)
        w_acc = bbox_acc[2] - bbox_acc[0]
        
        # Рисуем подложку под никнейм (небольшое затемнение)
        draw.text((width - w_acc - 52, height - 98), acc_text, font=font_acc, fill=(0, 0, 0, 150))
        draw.text((width - w_acc - 50, height - 100), acc_text, font=font_acc, fill="white")

        out = Image.alpha_composite(img, txt_layer)
        return out.convert("RGB")