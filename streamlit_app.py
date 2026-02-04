
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
""", unsafe_allow_html=True)

# Leer el archivo index.html generado
def load_html():
    if not os.path.exists("index.html"):
        return "<h1>Error: index.html no encontrado. Asegúrese de que el archivo existe en la raíz del proyecto.</h1>"
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# Renderizar la aplicación React dentro de un iframe de Streamlit
html_content = load_html()
# Aumentamos la altura para acomodar el calendario y permitimos el scroll
components.html(html_content, height=1200, scrolling=True)

st.info("Nota: Los datos se guardan localmente en su navegador. Para generar el Word apaisado, use el botón superior.")
