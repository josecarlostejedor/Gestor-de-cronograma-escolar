
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
API_KEY = "$2a$10$RPxoHbj3Z7oFeHcVX9KXNeQSlPDUcN/a0C1n7bFO6RcsNLROAwRaq"
BIN_ID = "6986233f43b1c97be96a93ee"
PASSWORD_CORRECTA = "1234"

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
    except Exception:
        return []

def save_to_cloud(data):
    try:
        url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
        headers = {"Content-Type": "application/json", "X-Master-Key": API_KEY}
        response = requests.put(url, headers=headers, json=data)
        return response.status_code == 200
    except Exception:
        return False

# --- EXPORTACIÓN A WORD ---
def generate_docx(activities):
    doc = Document()
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width, section.page_height = section.page_height, section.page_width

    title = doc.add_heading('Semana Cultural - IES Lucía de Medrano', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    table = doc.add_table(rows=1, cols=len(DAYS) + 1)
    table.style = 'Table Grid'
    
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Hora'
    for i, day in enumerate(DAYS):
        hdr_cells[i+1].text = day

    for slot_idx, slot in enumerate(TIME_SLOTS):
        row_cells = table.add_row().cells
        row_cells[0].text = f"{slot['label']}\n{slot['time']}"
        
        if slot['is_recess']:
            for i in range(1, len(DAYS) + 1):
                cell = row_cells[i]
                cell.text = "RECREO"
                from docx.oxml.ns import qn
                from docx.oxml import OxmlElement
                shading_elm = OxmlElement('w:shd')
                shading_elm.set(qn('w:fill'), "FFFBEB")
                cell._tc.get_or_add_tcPr().append(shading_elm)
        else:
            for day_idx, day in enumerate(DAYS):
                cell_acts = [a for a in activities if a['dayIndex'] == day_idx and a['slotIndex'] == slot_idx]
                cell = row_cells[day_idx+1]
                
                for act in cell_acts:
                    p = cell.add_paragraph()
                    p.add_run("Act: ").bold = True
                    p.add_run(act.get('title', ''))
                    p = cell.add_paragraph()
                    p.add_run("Dpt: ").bold = True
                    p.add_run(act.get('department', ''))
                    p = cell.add_paragraph()
                    p.add_run("Prof: ").bold = True
                    p.add_run(act.get('teacher', ''))
                    p = cell.add_paragraph()
                    p.add_run("Grp: ").bold = True
                    p.add_run(act.get('group', ''))
                    p = cell.add_paragraph()
                    p.add_run("Lug: ").bold = True
                    p.add_run(act.get('location', ''))
                    cell.add_paragraph()

    target = BytesIO()
    doc.save(target)
    return target.getvalue()

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Calendario IES Lucía de Medrano", layout="wide")

st.markdown("""
    <style>
    .activity-card {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        border-left: 4px solid #4f46e5;
        margin-bottom: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .header-day { text-align: center; font-weight: bold; background: #f3f4f6; padding: 8px; border-radius: 4px; }
    .recess-row { background-color: #fffbeb; text-align: center; font-weight: bold; color: #b45309; padding: 10px; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

if 'activities' not in st.session_state:
    st.session_state.activities = load_from_cloud()

# Sidebar para administración
with st.sidebar:
    st.title("⚙️ Gestión")
    
    with st.form("new_activity", clear_on_submit=True):
        st.subheader("Añadir Actividad")
        title = st.text_input("Actividad")
        dept = st.text_input("Departamento")
        teacher = st.text_input("Profesor")
        group = st.text_input("Grupo")
        room = st.text_input("Lugar")
        day_name = st.selectbox("Día", DAYS)
        hour_label = st.selectbox("Hora", [s['label'] for s in TIME_SLOTS if not s['is_recess']])
        
        if st.form_submit_button("🚀 Guardar"):
            if title:
                new_act = {
                    "id": str(uuid.uuid4()),
                    "title": title, "department": dept, "teacher": teacher, 
                    "group": group, "location": room,
                    "dayIndex": DAYS.index(day_name),
                    "slotIndex": next(i for i, s in enumerate(TIME_SLOTS) if s['label'] == hour_label)
                }
                st.session_state.activities.append(new_act)
                save_to_cloud(st.session_state.activities)
                st.rerun()

    st.divider()
    st.subheader("🔐 Administración")
    admin_pwd = st.text_input("Clave de seguridad", type="password")
    es_admin = (admin_pwd == PASSWORD_CORRECTA)

    if es_admin:
        st.success("Modo Administrador Activo")
        word_data = generate_docx(st.session_state.activities)
        st.download_button("📥 Descargar Word", data=word_data, file_name="Horario_Semana_Cultural.docx", use_container_width=True)
        if st.button("⚠️ BORRAR TODO EL CRONOGRAMA", type="primary", use_container_width=True):
            st.session_state.activities = []
            save_to_cloud([])
            st.rerun()
    else:
        st.info("Introduce la clave para borrar actividades o descargar el Word.")

st.title("🗓️ Semana Cultural - IES Lucía de Medrano")

cols = st.columns([1] + [2] * 5)
cols[0].markdown("<div class='header-day'>HORA</div>", unsafe_allow_html=True)
for i, day in enumerate(DAYS):
    cols[i+1].markdown(f"<div class='header-day'>{day}</div>", unsafe_allow_html=True)

for slot_idx, slot in enumerate(TIME_SLOTS):
    row = st.columns([1] + [2] * 5)
    with row[0]:
        st.markdown(f"**{slot['label']}**\n\n{slot['time']}")
    
    if slot['is_recess']:
        st.markdown("<div class='recess-row'>RECREO</div>", unsafe_allow_html=True)
        continue

    for day_idx in range(len(DAYS)):
        with row[day_idx+1]:
            cell_acts = [a for a in st.session_state.activities if a['dayIndex'] == day_idx and a['slotIndex'] == slot_idx]
            for act in cell_acts:
                st.markdown(f"""
                    <div class='activity-card'>
                        <div style='font-weight:bold;'>{act['title']}</div>
                        <div style='font-size:0.75rem;'>{act['department']} | {act['group']}<br>📍 {act['location']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Botón de eliminar condicional al password de la barra lateral
                if st.button("Eliminar", key=f"del_{act['id']}"):
                    if es_admin:
                        st.session_state.activities = [a for a in st.session_state.activities if a['id'] != act['id']]
                        save_to_cloud(st.session_state.activities)
                        st.rerun()
                    else:
                        st.error("Clave requerida en el panel lateral")
