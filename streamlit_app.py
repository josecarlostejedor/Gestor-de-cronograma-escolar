import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(layout="wide", page_title="IES Lucía de Medrano", page_icon="📅")

def load_app():
    # Leer el archivo index.html
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
            
        # Para que Streamlit sirva el archivo index.tsx local, 
        # lo inyectamos o nos aseguramos de que esté en el mismo directorio.
        # En este entorno, servimos el HTML que llama al index.tsx
        
        # Inyectar estilos para que el iframe ocupe todo
        st.markdown("""
            <style>
                iframe {
                    width: 100%;
                    height: 95vh;
                    border: none;
                }
                .stApp {
                    overflow: hidden;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Servir el componente HTML
        # Nota: index.tsx debe estar en la misma carpeta que index.html en GitHub
        components.html(html_content, height=1200, scrolling=True)
    else:
        st.error("No se encontró el archivo index.html")

if __name__ == "__main__":
    load_app()
