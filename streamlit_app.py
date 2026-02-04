
import streamlit as st
import streamlit.components.v1 as components
import os

# Configuración de la página
st.set_page_config(
    page_title="Semana Cultural IES Lucía de Medrano",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo para ocultar elementos innecesarios de Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px;}
    iframe {border: none;}
    </style>
""", unsafe_allow_index=True)

# Leer el archivo index.html generado
def load_html():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# Renderizar la aplicación React dentro de un iframe de Streamlit
html_content = load_html()
components.html(html_content, height=1000, scrolling=True)

st.info("Nota: Los datos se guardan localmente en su navegador. Para exportar, use el botón superior.")
