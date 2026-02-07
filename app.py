
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
    # Configurar orientación horizontal
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    # Intercambiar ancho y alto para landscape real
    old_width = section.page_width
    old_height = section.page_height
    section.page_width = old_height
    section.page_height = old_width

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

# CSS para estética
st.markdown("""
    <style>
    .stButton>button { border-radius: 8px; font-weight: bold; }
    .activity-card {
        background-color: white;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #4f46e5;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
        color: #1f2937;
    }
    .slot-time { font-size: 0.75rem; color: #6b7280; font-weight: bold; }
    .recess-row { 
        background-color: #fffbeb; 
        text-align: center; 
        font-weight: bold; 
        color: #b45309; 
        padding: 15px;
        border-radius: 8px;
        letter-spacing: 0.2em;
    }
    .header-day { text-align: center; font-weight: bold; color: #1e1b4b; background: #f3f4f6; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# Inicializar estado de las actividades
if 'activities' not in st.session_state:
    with st.spinner("Sincronizando con la nube..."):
        st.session_state.activities = load_from_cloud()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Panel de Gestión")
    
    # Formulario para nuevas actividades
    with st.form("new_activity", clear_on_submit=True):
        st.subheader("Añadir Actividad")
        title = st.text_input("Nombre de la actividad")
        dept = st.text_input("Departamento")
        teacher = st.text_input("Profesor")
        group = st.text_input("Grupo")
        room = st.text_input("Lugar")
        
        col_d, col_h = st.columns(2)
        day_name = col_d.selectbox("Día", DAYS)
        hour_label = col_h.selectbox("Hora", [s['label'] for s in TIME_SLOTS if not s['is_recess']])
        
        if st.form_submit_button("🚀 Guardar en Nube"):
            if title and dept and teacher:
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
                save_to_cloud(st.session_state.activities)
                st.success("Guardado correctamente")
                st.rerun()
            else:
                st.warning("Completa los campos principales")

    st.divider()

    # SECCIÓN DE ADMINISTRACIÓN PROTEGIDA
    st.subheader("🔐 Administración")
    admin_pwd = st.text_input("Contraseña de seguridad", type="password")

    if admin_pwd == PASSWORD_CORRECTA:
        st.success("Acceso concedido")
        
        # Botón de Descarga (Word)
        word_file = generate_docx(st.session_state.activities)
        st.download_button(
            label="📥 Descargar Horario (Word)",
            data=word_file,
            file_name=f"Calendario_Semana_Cultural_{datetime.now().strftime('%d_%m')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
        
        # Botón de Borrado Total
        if st.button("⚠️ BORRAR TODO EL CALENDARIO", type="primary", use_container_width=True):
            st.session_state.activities = []
            if save_to_cloud([]):
                st.success("Nube vaciada")
                st.rerun()
    elif admin_pwd:
        st.error("Contraseña incorrecta")

# --- CUERPO PRINCIPAL ---
st.title("🗓️ Semana Cultural - IES Lucía de Medrano")
st.caption(f"☁️ Datos sincronizados en tiempo real (ID: {BIN_ID})")

# Dibujar la tabla
header_cols = st.columns([1] + [2] * 5)
header_cols[0].markdown("<div class='header-day'>HORA</div>", unsafe_allow_html=True)
for i, day in enumerate(DAYS):
    header_cols[i+1].markdown(f"<div class='header-day'>{day}</div>", unsafe_allow_html=True)

for slot_idx, slot in enumerate(TIME_SLOTS):
    row_cols = st.columns([1] + [2] * 5)
    
    with row_cols[0]:
        st.markdown(f"**{slot['label']}**")
        st.markdown(f"<div class='slot-time'>{slot['time']}</div>", unsafe_allow_html=True)
    
    if slot['is_recess']:
        st.markdown("<div class='recess-row'>— RECREO —</div>", unsafe_allow_html=True)
        continue

    for day_idx in range(len(DAYS)):
        with row_cols[day_idx+1]:
            # Filtrar actividades para esta celda
            cell_acts = [a for a in st.session_state.activities if a['dayIndex'] == day_idx and a['slotIndex'] == slot_idx]
            for act in cell_acts:
                st.markdown(f"""
                    <div class='activity-card'>
                        <div style='font-weight:800; font-size:0.9rem;'>{act['title']}</div>
                        <div style='font-size:0.75rem; color:#4b5563;'>
                            🏢 {act['department']}<br>
                            👥 {act['group']}<br>
                            📍 {act['location']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                # Botón de borrar individual
                if st.button("Eliminar", key=f"del_{act['id']}", size="small"):
                    st.session_state.activities = [a for a in st.session_state.activities if a['id'] != act['id']]
                    save_to_cloud(st.session_state.activities)
                    st.rerun()

st.divider()
st.info("💡 Este calendario mantiene los datos aunque apagues el PC. Para descargar o borrar todo, usa la clave '1234' en el panel lateral.")
