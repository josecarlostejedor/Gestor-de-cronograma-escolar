
import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="Calendario IES Lucía de Medrano",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px;}
    iframe {border: none;}
    </style>
""", unsafe_allow_html=True)

def load_index():
    path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error: index.html no encontrado.</h1>"

html_content = load_index()
components.html(html_content, height=1200, scrolling=True)
