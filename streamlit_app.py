import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(layout="wide", page_title="IES Lucía de Medrano", page_icon="📅")

def load_app():
    # Estilo CSS para eliminar márgenes de Streamlit y forzar altura completa
    st.markdown("""
        <style>
            .main > div { padding: 0px; }
            iframe { width: 100%; height: 95vh !important; border: none; }
            header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Cargamos el HTML consolidado. Al estar todo en un solo archivo, 
        # no habrá errores de rutas relativas.
        components.html(html_content, height=1500, scrolling=True)
    else:
        st.error("Error: Archivo index.html no encontrado.")

if __name__ == "__main__":
    load_app()
