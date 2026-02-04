
import streamlit as st
import streamlit.components.v1 as components
import os

# Configuración de la página
st.set_page_config(
    page_title="Calendario IES Lucía de Medrano",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos para ocultar la interfaz de Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px;}
    iframe {border: none;}
    </style>
""", unsafe_allow_html=True)

def get_file_content(file_name):
    # Intentar varias rutas comunes en Streamlit Cloud
    paths_to_try = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name),
        os.path.join(os.getcwd(), file_name),
        file_name
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    return None

# Intentar cargar index.html
html_content = get_file_content("index.html")

if html_content:
    # Renderizar la aplicación
    components.html(html_content, height=1000, scrolling=True)
else:
    st.error("⚠️ No se pudo encontrar el archivo 'index.html'.")
    st.info("Asegúrate de que 'index.html' esté en la raíz de tu repositorio de GitHub, junto a 'streamlit_app.py'.")
    # Debug para el usuario
    st.write("Archivos detectados en el directorio actual:", os.listdir("."))

st.caption("Gestor Interno IES Lucía de Medrano. Clave: 1234")
