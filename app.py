import streamlit as st
from modules.ai_processor import ContentEngine
from io import BytesIO

st.set_page_config(page_title="SeiO: Premium Insta Engine", layout="wide")

st.sidebar.title("🚀 SeiO v3.5")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
account_name = st.sidebar.text_input("Ваш @никнейм", placeholder="username")

# Выбор шрифта в сайдбаре
selected_font = st.sidebar.selectbox(
    "Выберите шрифт для визуала:",
    ["Montserrat", "Bebas Neue", "Inter", "Oswald"]
)

if api_key:
    engine = ContentEngine(api_key)
    tab_trend, tab_create = st.tabs(["🔥 Радар Трендов", "🎨 Дизайн-Студия"])

    with tab_create:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            raw_input = st.text_area("Тема или текст поста:", height=150)
            if st.button("Сгенерировать идею и текст"):
                with st.spinner("Работаю..."):
                    post = engine.professional_rewrite(raw_input, "Эксперт")
                    hooks = engine.generate_visual_hooks(post)
                    st.session_state['final_text'] = post
                    # Берем первую строку из предложенных хуков как основной заголовок
                    st.session_state['suggested_hook'] = hooks.split('\n')[0].strip('12345. ')

            if 'final_text' in st.session_state:
                st.divider()
                # Поле для редактирования текста на картинке
                image_title = st.text_input("Текст на изображении (можно изменить):", 
                                          value=st.session_state.get('suggested_hook', ""))
                
                if st.button("Создать финальный пост с обложкой 📸"):
                    if not account_name:
                        st.error("Укажите никнейм в боковом меню!")
                    else:
                        with st.spinner("Генерирую фон и накладываю шрифт..."):
                            bg_url = engine.generate_image(st.session_state['final_text'])
                            final_img = engine.overlay_text(bg_url, image_title, account_name, selected_font)
                            st.session_state['processed_img'] = final_img

        with col2:
            if 'final_text' in st.session_state:
                if 'processed_img' in st.session_state:
                    st.image(st.session_state['processed_img'], use_container_width=True)
                    
                    # Подготовка к скачиванию
                    buf = BytesIO()
                    st.session_state['processed_img'].save(buf, format="JPEG", quality=95)
                    st.download_button(
                        label="📥 Скачать готовый пост",
                        data=buf.getvalue(),
                        file_name=f"insta_{selected_font}.jpg",
                        mime="image/jpeg"
                    )

                st.subheader("📝 Текст поста:")
                st.write(st.session_state['final_text'])