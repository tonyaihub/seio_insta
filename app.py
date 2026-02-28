import streamlit as st
import openai
import requests
import textwrap
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from duckduckgo_search import DDGS

# --- КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(page_title="SeiO: Insta Engine", layout="wide", page_icon="📸")

# --- ЛОГИКА AI И ОБРАБОТКИ ---
class SeiOEngine:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    def get_instagram_trends(self, keywords):
        """Поиск трендов в Instagram за 24 часа"""
        search_query = f"site:instagram.com {keywords} (reels OR viral OR trending)"
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(search_query, timelimit='d', max_results=7)]
        
        if not results:
            return "Ничего не найдено. Попробуйте изменить ключевые слова."

        context = "\n".join([f"- {r['body']}" for r in results])
        prompt = f"Проанализируй эти инста-тренды за 24 часа по запросу '{keywords}':\n{context}\nВыдели 3 горячих темы и предложи сценарий Reels для каждой."
        
        res = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content

    def professional_rewrite(self, text, tone):
        """Рерайт текста"""
        prompt = f"Сделай профессиональный рерайт текста для Instagram в стиле {tone}. Добавь крючок в начале и CTA в конце. Текст: {text}"
        res = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content

    def generate_visual_hooks(self, text):
        """Генерация короткого заголовка для картинки"""
        prompt = f"На основе текста придумай ОДИН очень короткий (до 4 слов) заголовок для обложки. Выдай только этот заголовок. Текст: {text}"
        res = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content.strip(' "')

    def generate_image(self, post_text):
        """DALL-E 3 генерация фона"""
        prompt = f"Aesthetic high-quality Instagram background, cinematic lighting, minimalistic, no text, related to: {post_text[:100]}"
        res = self.client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", n=1)
        return res.data[0].url

    def overlay_text(self, image_url, title, account_name, font_name):
        """Накладывание текста на изображение"""
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        font_paths = {
            "Montserrat": "fonts/Montserrat-Bold.ttf",
            "Bebas Neue": "fonts/BebasNeue-Regular.ttf",
            "Inter": "fonts/Inter-Black.ttf",
            "Oswald": "fonts/Oswald-Medium.ttf"
        }
        
        f_path = font_paths.get(font_name)
        try:
            font_title = ImageFont.truetype(f_path, 80) if os.path.exists(f_path) else ImageFont.load_default()
            font_acc = ImageFont.truetype(f_path, 35) if os.path.exists(f_path) else ImageFont.load_default()
        except:
            font_title = ImageFont.load_default()
            font_acc = ImageFont.load_default()

        # Заголовок сверху по центру
        lines = textwrap.wrap(title.upper(), width=18)
        y_text = 100
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_title)
            w = bbox[2] - bbox[0]
            draw.text(((1024 - w) / 2 + 3, y_text + 3), line, font=font_title, fill=(0, 0, 0, 160)) # Тень
            draw.text(((1024 - w) / 2, y_text), line, font=font_title, fill="white")
            y_text += 90

        # Аккаунт снизу справа
        acc_text = f"@{account_name.replace('@', '')}"
        bbox_acc = draw.textbbox((0, 0), acc_text, font=font_acc)
        w_acc = bbox_acc[2] - bbox_acc[0]
        draw.text((1024 - w_acc - 53, 943), acc_text, font=font_acc, fill=(0, 0, 0, 150))
        draw.text((1024 - w_acc - 50, 940), acc_text, font=font_acc, fill="white")

        return Image.alpha_composite(img, txt_layer).convert("RGB")

# --- ИНТЕРФЕЙС STREAMLIT ---
st.sidebar.title("📸 SeiO: Insta Edition")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
account_name = st.sidebar.text_input("Ваш Instagram @ник", placeholder="username")
selected_font = st.sidebar.selectbox("Шрифт:", ["Montserrat", "Bebas Neue", "Inter", "Oswald"])

if api_key:
    engine = SeiOEngine(api_key)
    tab1, tab2 = st.tabs(["🔥 Радар Трендов 24ч", "🎨 Создание Контента"])

    # Вкладка 1: Тренды
    with tab1:
        st.header("Поиск трендов в Instagram")
        keywords = st.text_input("Введите до 5 ключевых слов:", placeholder="дизайн интерьера минимализм")
        if st.button("Найти Хайп 🚀"):
            if len(keywords.split()) <= 5:
                with st.spinner("Сканирую Instagram за последние 24 часа..."):
                    trend_report = engine.get_instagram_trends(keywords)
                    st.markdown(trend_report)
                    st.session_state['last_trend'] = trend_report
            else:
                st.error("Пожалуйста, не более 5 слов.")

    # Вкладка 2: Редактор
    with tab2:
        col_edit, col_prev = st.columns([1, 1])
        
        with col_edit:
            st.subheader("Настройка поста")
            raw_text = st.text_area("О чем пишем? (или вставьте идею из трендов)", height=150)
            tone = st.select_slider("Стиль:", options=["Эксперт", "Дерзкий", "Минимализм"])
            
            if st.button("1. Сгенерировать Текст ✨"):
                with st.spinner("Пишу..."):
                    final_text = engine.professional_rewrite(raw_text, tone)
                    suggested_hook = engine.generate_visual_hooks(final_text)
                    st.session_state['st_final_text'] = final_text
                    st.session_state['st_hook'] = suggested_hook

            if 'st_final_text' in st.session_state:
                st.divider()
                img_title = st.text_input("Заголовок на картинке:", value=st.session_state.get('st_hook', ""))
                if st.button("2. Создать Обложку 🎨"):
                    if not account_name:
                        st.warning("Укажите ник в боковом меню!")
                    else:
                        with st.spinner("Генерация DALL-E 3 и наложение текста..."):
                            bg_url = engine.generate_image(st.session_state['st_final_text'])
                            final_img = engine.overlay_text(bg_url, img_title, account_name, selected_font)
                            st.session_state['st_processed_img'] = final_img

        with col_prev:
            if 'st_final_text' in st.session_state:
                st.subheader("Предпросмотр")
                if 'st_processed_img' in st.session_state:
                    st.image(st.session_state['st_processed_img'], use_container_width=True)
                    
                    # Кнопка скачивания
                    buf = BytesIO()
                    st.session_state['st_processed_img'].save(buf, format="JPEG", quality=95)
                    st.download_button("📥 Скачать готовый пост", buf.getvalue(), "post.jpg", "image/jpeg")
                
                st.write("**Текст для описания:**")
                st.info(st.session_state['st_final_text'])
else:
    st.info("👋 Добро пожаловать! Введите OpenAI API Key в боковом меню, чтобы начать.")

# Инструкция по шрифтам
if not os.path.exists("fonts"):
    st.warning("⚠️ Папка 'fonts' не найдена. Создайте её и добавьте .ttf файлы выбранных шрифтов.")