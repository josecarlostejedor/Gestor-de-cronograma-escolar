
import streamlit as st
import streamlit.components.v1 as components
import os

# Configuración básica de Streamlit
st.set_page_config(
    page_title="Calendario Semana Cultural",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar elementos de Streamlit y forzar estilos limpios
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px;}
    iframe {border: none;}
    </style>
""", unsafe_allow_html=True)

# Función para cargar el HTML de la aplicación
def load_app():
    if not os.path.exists("index.html"):
        return "<h1>Error: El archivo index.html no se encuentra en el repositorio.</h1>"
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# Inyectar la aplicación React
app_html = load_app()
components.html(app_html, height=1200, scrolling=True)

# Mensaje de ayuda en la parte inferior de Streamlit
st.caption("IES Lucía de Medrano - Herramienta de Gestión Interna. Los cambios se guardan automáticamente en su navegador.")
