
import streamlit as st
import streamlit.components.v1 as components
import os

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Calendario Semana Cultural - IES Lucía de Medrano",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos para limpiar la interfaz de Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px;}
    iframe {border: none;}
    </style>
""", unsafe_allow_html=True)

# Función para cargar el archivo HTML con una ruta absoluta robusta
def load_app():
    # Obtener la ruta del directorio donde se encuentra este script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, "index.html")
    
    if not os.path.exists(index_path):
        return f"<h1>Error: index.html no encontrado.</h1><p>Buscado en: {index_path}</p>"
    
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

# Renderizar la aplicación
app_html = load_app()

# Nota: El height de 1200 es para asegurar que quepa el calendario sin doble scroll
components.html(app_html, height=1200, scrolling=True)

st.caption("Planificador Interno IES Lucía de Medrano. Clave de exportación/borrado: 1234")
