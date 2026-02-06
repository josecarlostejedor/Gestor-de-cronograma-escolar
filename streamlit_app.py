
import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="Gestor IES Lucía de Medrano",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo para ocultar elementos de Streamlit y maximizar el espacio
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px;}
    iframe {border: none; width: 100%;}
    </style>
""", unsafe_allow_html=True)

def load_index():
    path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error Fatal: index.html no encontrado en el servidor.</h1>"

html_content = load_index()
# El componente HTML de Streamlit admite descargas por defecto en versiones recientes
components.html(html_content, height=1300, scrolling=True)
