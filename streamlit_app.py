import streamlit as st
import streamlit.components.v1 as components
import os

# Configuración de página Streamlit
st.set_page_config(
    layout="wide", 
    page_title="Calendario IES Lucía de Medrano", 
    page_icon="📅",
    initial_sidebar_state="collapsed"
)

def load_app():
    # Eliminar espacios vacíos de Streamlit mediante CSS inyectado
    st.markdown("""
        <style>
            .main > div { padding: 0px; }
            iframe { width: 100%; height: 98vh !important; border: none; }
            #MainMenu, header, footer { visibility: hidden; }
            .stApp { overflow: hidden; }
        </style>
    """, unsafe_allow_html=True)

    # Verificar si el archivo index.html existe
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Servir el HTML consolidado. 
        # scrolling=True permite desplazarse si el calendario es muy largo.
        components.html(html_content, height=2000, scrolling=True)
    else:
        st.error("Error crítico: No se encontró el archivo 'index.html' en el repositorio.")
        st.info("Asegúrate de que index.html esté en la carpeta principal de tu GitHub.")

if __name__ == "__main__":
    load_app()
