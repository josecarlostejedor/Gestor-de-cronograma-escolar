
import streamlit as st
import requests
import json
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from io import BytesIO
import uuid
from datetime import datetime

# --- CONFIGURACIÓN DE LA NUBE (JSONBin.io) ---
# Usamos las mismas credenciales que en la versión React para que los datos sean compartidos
API_KEY = "$2a$10$RPxoHbj3Z7oFeHcVX9KXNeQSlPDUcN/a0C1n7bFO6RcsNLROAwRaq"
BIN_ID = "6986233f43b1c97be96a93ee"
PASSWORD_SEGURIDAD = "1234"

# --- CONSTANTES ---
DAYS = ["Lunes 23", "Martes 24", "Miércoles 25", "Jueves 26", "Viernes 27"]
TIME_SLOTS = [
    {"label": "1ª Hora", "time": "08:50 - 09:45", "is_recess": False},
    {"label": "2ª Hora", "time": "09:45 - 10:40", "is_recess": False},
    {"label": "3ª Hora", "time": "10:40 - 11:30", "is_recess": False},
    {"label": "Recreo", "time": "11:30 - 11:55", "is_recess": True},
    {"label": "4ª Hora", "time": "11:55 - 12:50", "is_recess": False},
    {"label": "5ª Hora", "time": "12:50 - 13:45", "is_recess": False},
    {"label": "6ª Hora", "time": "13:45 - 14:35", "is_recess": False},
]

# --- FUNCIONES DE PERSISTENCIA ---
def load_from_cloud():
    try:
        url = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"
        headers = {"X-Master-Key": API_KEY, "X-Bin-Meta": "false"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error cargando de la nube: {e}")
        return []

def save_to_cloud(data):
    try:
        url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
        headers = {"Content-Type": "application/json", "X-Master-Key": API_KEY}
        response = requests.put(url, headers=headers, json=data)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error guardando en la nube: {e}")
        return False

# --- EXPORTACIÓN A WORD ---
def generate_docx(activities):
    doc = Document()
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    new_width, new_height = section.page_height, section.page_width
    section.page_width = new_width
    section.page_height = new_height

    title = doc.add_heading('Semana Cultural - IES Lucía de Medrano', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    table = doc.add_table(rows=1, cols=len(DAYS) + 1)
    table.style = 'Table Grid'
    
    # Encabezados
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Hora'
    for i, day in enumerate(DAYS):
        hdr_cells[i+1].text = day

    # Filas de tiempo
    for slot_idx, slot in enumerate(TIME_SLOTS):
        row_cells = table.add_row().cells
        row_cells[0].text = f"{slot['label']}\n{slot['time']}"
        
        if slot['is_recess']:
            for i in range(1, len(DAYS) + 1):
                row_cells[i].text = "RECREO"
        else:
            for day_idx, day in enumerate(DAYS):
                cell_acts = [a for a in activities if a['dayIndex'] == day_idx and a['slotIndex'] == slot_idx]
                text = ""
                for act in cell_acts:
                    text += f"• {act['title']}\n({act['department']})\nProf: {act['teacher']}\n{act['group']} - {act['location']}\n\n"
                row_cells[day_idx+1].text = text.strip()

    target = BytesIO()
    doc.save(target)
    return target.getvalue()

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Calendario IES Lucía de Medrano", layout="wide")

# CSS para estética moderna
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .activity-card {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        border-left: 5px solid #4f46e5;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .slot-time { font-size: 0.8rem; color: #6b7280; font-weight: bold; }
    .recess-row { background-color: #fffbeb; text-align: center; font-weight: bold; color: #b45309; }
    </style>
""", unsafe_allow_html=True)

# Inicializar estado
if 'activities' not in st.session_state:
    with st.spinner("Sincronizando con la nube..."):
        st.session_state.activities = load_from_cloud()

# --- SIDEBAR: GESTIÓN ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2693/2693507.png", width=100)
    st.title("Gestión de Actividades")
    
    with st.form("new_activity", clear_on_submit=True):
        st.subheader("Nueva Entrada")
        title = st.text_input("Título de la actividad")
        dept = st.text_input("Departamento")
        teacher = st.text_input("Profesor")
        group = st.text_input("Grupo")
        room = st.text_input("Aula/Lugar")
        
        col1, col2 = st.columns(2)
        day_name = col1.selectbox("Día", DAYS)
        hour_label = col2.selectbox("Hora", [s['label'] for s in TIME_SLOTS if not s['is_recess']])
        
        submitted = st.form_submit_button("Añadir a la Nube")
        
        if submitted and title:
            day_idx = DAYS.index(day_name)
            slot_idx = next(i for i, s in enumerate(TIME_SLOTS) if s['label'] == hour_label)
            
            new_act = {
                "id": str(uuid.uuid4()),
                "title": title,
                "department": dept,
                "teacher": teacher,
                "group": group,
                "location": room,
                "dayIndex": day_idx,
                "slotIndex": slot_idx
            }
            
            st.session_state.activities.append(new_act)
            if save_to_cloud(st.session_state.activities):
                st.success("¡Guardado permanentemente!")
                st.rerun()

    st.divider()
    
    # Exportar
    if st.button("📥 Descargar Horario (Word)"):
        pwd = st.text_input("Clave de exportación", type="password")
        if pwd == PASSWORD_SEGURIDAD:
            docx_data = generate_docx(st.session_state.activities)
            st.download_button(
                label="Confirmar Descarga",
                data=docx_data,
                file_name="Semana_Cultural_Lucia_Medrano.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        elif pwd:
            st.error("Clave incorrecta")

    # Borrar todo
    if st.button("🗑️ Borrar Todo"):
        pwd = st.text_input("Clave maestra para borrar", type="password", key="del_all")
        if pwd == PASSWORD_SEGURIDAD:
            st.session_state.activities = []
            save_to_cloud([])
            st.rerun()

# --- ÁREA PRINCIPAL ---
st.title("🗓️ Semana Cultural - IES Lucía de Medrano")
st.caption(f"Sincronizado con base de datos en la nube (ID: {BIN_ID})")

# Crear la tabla visual
cols = st.columns([1] + [2] * 5)
cols[0].write("**HORA**")
for i, day in enumerate(DAYS):
    cols[i+1].write(f"**{day}**")

for slot_idx, slot in enumerate(TIME_SLOTS):
    cols = st.columns([1] + [2] * 5)
    
    # Columna de Hora
    with cols[0]:
        st.markdown(f"**{slot['label']}**")
        st.markdown(f"<div class='slot-time'>{slot['time']}</div>", unsafe_allow_html=True)
    
    # Recreo
    if slot['is_recess']:
        st.markdown("<div class='recess-row'>— RECREO —</div>", unsafe_allow_html=True)
        continue

    # Días
    for day_idx in range(len(DAYS)):
        with cols[day_idx+1]:
            cell_acts = [a for a in st.session_state.activities if a['dayIndex'] == day_idx and a['slotIndex'] == slot_idx]
            for act in cell_acts:
                with st.container():
                    st.markdown(f"""
                        <div class='activity-card'>
                            <b>{act['title']}</b><br>
                            <small>{act['department']} | {act['group']}</small><br>
                            <small>📍 {act['location']}</small>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("❌", key=f"del_{act['id']}"):
                        st.session_state.activities = [a for a in st.session_state.activities if a['id'] != act['id']]
                        save_to_cloud(st.session_state.activities)
                        st.rerun()

st.info("💡 Todos los cambios se guardan automáticamente en la nube. Puedes cerrar el navegador o apagar el PC sin perder nada.")
