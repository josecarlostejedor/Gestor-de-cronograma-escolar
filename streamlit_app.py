import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(layout="wide", page_title="IES Lucía de Medrano", page_icon="📅")

def load_app():
    # Estilos para que el calendario ocupe toda la pantalla de Streamlit
    st.markdown("""
        <style>
            .stApp { overflow: hidden; }
            .main > div { padding: 0px !important; }
            iframe { width: 100%; height: 98vh !important; border: none; }
            header { visibility: hidden; }
            footer { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        # Inyectar el HTML directamente
        components.html(html_content, height=2000, scrolling=True)
    else:
        st.error("Error: No se encontró el archivo index.html")

if __name__ == "__main__":
    load_app()
