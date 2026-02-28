import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image

# Настройка страницы
st.set_page_config(page_title="SeiO: Insta Edition", layout="wide", page_icon="📸")

# --- СТИЛИЗАЦИЯ (Custom CSS) ---
st.markdown("""
    <style>
    .insta-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-top: 20px;
    }
    .grid-item {
        aspect-ratio: 1 / 1;
        border: 1px solid #ddd;
        border-radius: 5px;
        overflow: hidden;
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ИНТЕРФЕЙС (Sidebar) ---
st.sidebar.title("🚀 SeiO Insta")
menu = st.sidebar.radio("Меню", ["Визуальный план", "Генератор контента", "Аналитика", "Настройки"])

# --- МОДУЛЬ 1: ВИЗУАЛЬНЫЙ ПЛАН (GRID) ---
if menu == "Визуальный план":
    st.header("🖼 Планировщик ленты")
    
    # Имитация данных из БД
    posts = [
        {"id": 1, "img": "https://via.placeholder.com/400/FF5733/fff", "status": "Опубликовано"},
        {"id": 2, "img": "https://via.placeholder.com/400/33FF57/fff", "status": "Опубликовано"},
        {"id": 3, "img": "https://via.placeholder.com/400/3357FF/fff", "status": "Запланировано"},
        {"id": 4, "img": "https://via.placeholder.com/400/F333FF/fff", "status": "Черновик"},
    ]

    # Отображение сетки 3хN
    cols = st.columns(3)
    for idx, post in enumerate(posts):
        with cols[idx % 3]:
            st.image(post['img'], use_column_width=True)
            st.caption(f"Статус: {post['status']}")
            if st.button(f"Правка #{post['id']}", key=f"edit_{post['id']}"):
                st.info(f"Редактируем пост {post['id']}")

    st.divider()
    st.button("➕ Добавить пост в сетку")

# --- МОДУЛЬ 2: ГЕНЕРАТОР КОНТЕНТА ---
elif menu == "Генератор контента":
    st.header("✍️ AI Креатор")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Настройки идеи")
        topic = st.text_input("О чем будет пост/Reels?", placeholder="Например: 5 ошибок в дизайне интерьера")
        format_type = st.selectbox("Формат", ["Reels (сценарий)", "Пост в ленту", "Цепочка Stories"])
        tone = st.select_slider("Тон", options=["Дружелюбный", "Экспертный", "Провокационный"])
        
        if st.button("Сгенерировать концепт ✨"):
            with st.spinner('Искин SeiO думает...'):
                # Здесь будет вызов из ai_logic.py
                st.session_state['ai_result'] = "Вот ваш крутой сценарий для Reels..." 

    with col2:
        st.subheader("Результат")
        if 'ai_result' in st.session_state:
            st.write(st.session_state['ai_result'])
            st.button("💾 Сохранить в черновики")
            st.button("🎨 Создать обложку (DALL-E 3)")

# --- МОДУЛЬ 3: НАСТРОЙКИ ---
elif menu == "Настройки":
    st.header("⚙️ Подключение аккаунтов")
    st.text_input("OpenAI API Key", type="password")
    st.text_input("Instagram Business ID")
    st.button("Проверить соединение")