import streamlit as st
import streamlit.components.v1 as components
import json

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Calendario Escolar Conectado",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ocultar elementos propios de Streamlit
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem; }
        header { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR PARA CONFIGURACIÓN DE NUBE ---
st.sidebar.title("☁️ Sincronización")
st.sidebar.markdown("Para compartir datos entre dispositivos, configura [JSONBin.io](https://jsonbin.io/):")

use_cloud = st.sidebar.checkbox("Activar Modo Nube", value=False)
api_key = ""
bin_id = ""

if use_cloud:
    api_key = st.sidebar.text_input("API Key (Master Key)", type="password", help="Tu X-Master-Key de JSONBin")
    bin_id = st.sidebar.text_input("Bin ID", help="El ID del Bin que creaste")
    
    if api_key and bin_id:
        st.sidebar.success("Configuración lista. Los datos se guardarán en la nube.")
    else:
        st.sidebar.warning("Introduce las claves para sincronizar.")
else:
    st.sidebar.info("Modo Local: Los datos solo se guardan en este dispositivo.")

# Preparamos la configuración para inyectarla en JS
cloud_config = json.dumps({
    "enabled": use_cloud and len(api_key) > 0 and len(bin_id) > 0,
    "apiKey": api_key,
    "binId": bin_id
})

# El código HTML/JS completo (Usamos string normal, no f-string, para evitar conflictos con las llaves de JS)
html_code = """
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Calendario Escolar</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="importmap">
      {
        "imports": {
          "react": "https://esm.sh/react@18.2.0",
          "react-dom/client": "https://esm.sh/react-dom@18.2.0/client",
          "lucide-react": "https://esm.sh/lucide-react@0.330.0",
          "docx": "https://esm.sh/docx@8.5.0",
          "file-saver": "https://esm.sh/file-saver@2.0.5"
        }
      }
    </script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  </head>
  <body class="bg-gray-50 text-gray-900">
    <div id="root"></div>

    <script type="text/babel" data-type="module">
      import React, { useState, useEffect } from 'react';
      import ReactDOM from 'react-dom/client';
      import { Plus, Calendar as CalendarIcon, MapPin, Users, Building2, X, Download, Lock, Trash2, AlertTriangle, Save, Cloud, CloudOff, Loader2 } from 'lucide-react';
      import { Document, Packer, Paragraph, Table, TableCell, TableRow, WidthType, TextRun, AlignmentType, HeadingLevel, PageOrientation, BorderStyle } from "docx";
      import FileSaver from "file-saver";

      // --- CONFIGURACIÓN DE NUBE INYECTADA DESDE PYTHON ---
      const CLOUD_CONFIG = __CLOUD_CONFIG__;

      // --- TYPES & CONSTANTS ---
      const DAYS = ["Lunes 23", "Martes 24", "Miércoles 25", "Jueves 26", "Viernes 27"];
      const TIME_SLOTS = [
        { id: 0, label: "1ª Hora", time: "08:50 - 09:45" },
        { id: 1, label: "2ª Hora", time: "09:45 - 10:40" },
        { id: 2, label: "3ª Hora", time: "10:40 - 11:30" },
        { id: 3, label: "Recreo", time: "11:30 - 11:55", isRecess: true },
        { id: 4, label: "4ª Hora", time: "11:55 - 12:50" },
        { id: 5, label: "5ª Hora", time: "12:50 - 13:45" },
        { id: 6, label: "6ª Hora", time: "13:45 - 14:35" },
      ];

      // --- STORAGE SERVICE ---
      const storageService = {
        async load() {
          if (CLOUD_CONFIG.enabled) {
            try {
              const response = await fetch(`https://api.jsonbin.io/v3/b/${CLOUD_CONFIG.binId}/latest`, {
                headers: { 'X-Master-Key': CLOUD_CONFIG.apiKey }
              });
              if (!response.ok) throw new Error('Error loading from cloud');
              const data = await response.json();
              return Array.isArray(data.record) ? data.record : [];
            } catch (error) {
              console.error("Cloud load error:", error);
              alert("Error cargando datos de la nube. Verifica tus claves.");
              return [];
            }
          } else {
            const saved = localStorage.getItem('school_calendar_activities');
            return saved ? JSON.parse(saved) : [];
          }
        },

        async save(activities) {
          if (CLOUD_CONFIG.enabled) {
            try {
              await fetch(`https://api.jsonbin.io/v3/b/${CLOUD_CONFIG.binId}`, {
                method: 'PUT',
                headers: {
                  'Content-Type': 'application/json',
                  'X-Master-Key': CLOUD_CONFIG.apiKey
                },
                body: JSON.stringify(activities)
              });
              return true;
            } catch (error) {
              console.error("Cloud save error:", error);
              return false;
            }
          } else {
            localStorage.setItem('school_calendar_activities', JSON.stringify(activities));
            return true;
          }
        }
      };

      // --- WORD GENERATOR ---
      const generateWordDocument = async (activities) => {
        const getActivitiesForCell = (dayIndex, slotIndex) => activities.filter(a => a.dayIndex === dayIndex && a.slotIndex === slotIndex);
        
        const headerRow = new TableRow({
          children: [
            new TableCell({ width: { size: 10, type: WidthType.PERCENTAGE }, children: [new Paragraph({ text: "Hora", style: "TableHeader" })], shading: { fill: "E0E0E0" } }),
            ...DAYS.map(day => new TableCell({ width: { size: 18, type: WidthType.PERCENTAGE }, children: [new Paragraph({ text: day, style: "TableHeader", alignment: AlignmentType.CENTER })], shading: { fill: "E0E0E0" } }))
          ],
        });

        const dataRows = TIME_SLOTS.map(slot => {
          const isRecess = slot.isRecess;
          const timeCell = new TableCell({ children: [new Paragraph({ text: slot.label, bold: true }), new Paragraph({ text: slot.time, size: 20 })], shading: isRecess ? { fill: "FFF8DC" } : undefined, verticalAlign: "center" });

          if (isRecess) {
            const recessCells = DAYS.map(() => new TableCell({ children: [new Paragraph({ text: "RECREO", alignment: AlignmentType.CENTER, bold: true })], shading: { fill: "FFF8DC" }, verticalAlign: "center" }));
            return new TableRow({ children: [timeCell, ...recessCells] });
          }

          const dayCells = DAYS.map((_, dayIndex) => {
            const cellActivities = getActivitiesForCell(dayIndex, slot.id);
            const paragraphs = cellActivities.length > 0 
              ? cellActivities.flatMap(act => [
                  new Paragraph({ children: [new TextRun({ text: `• ${act.title}`, bold: true })] }),
                  new Paragraph({ text: `  Dept: ${act.department}`, size: 18 }),
                  new Paragraph({ text: `  Grupo: ${act.group} | Lugar: ${act.location}`, size: 18 }),
                  new Paragraph({ text: "" }),
                ])
              : [new Paragraph({ text: "" })];
            return new TableCell({ children: paragraphs, verticalAlign: "top" });
          });
          return new TableRow({ children: [timeCell, ...dayCells] });
        });

        const doc = new Document({
          sections: [{
            properties: { page: { size: { orientation: PageOrientation.LANDSCAPE }, margin: { top: 1000, bottom: 1000, left: 1000, right: 1000 } } },
            children: [
              new Paragraph({ text: "Cronograma Semanal: 23-27 de Marzo", heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER, spacing: { after: 400 } }),
              new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: [headerRow, ...dataRows], borders: { top: { style: BorderStyle.SINGLE, size: 1, color: "000000" }, bottom: { style: BorderStyle.SINGLE, size: 1, color: "000000" }, left: { style: BorderStyle.SINGLE, size: 1, color: "000000" }, right: { style: BorderStyle.SINGLE, size: 1, color: "000000" }, insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: "000000" }, insideVertical: { style: BorderStyle.SINGLE, size: 1, color: "000000" } } }),
            ],
          }],
          styles: { paragraphStyles: [{ id: "TableHeader", name: "Table Header", basedOn: "Normal", next: "Normal", run: { bold: true, size: 24 }, paragraph: { alignment: AlignmentType.CENTER } }] },
        });
        const blob = await Packer.toBlob(doc);
        FileSaver.saveAs(blob, "Cronograma_Semanal_23-27_Marzo.docx");
      };

      // --- COMPONENTS ---
      const ActivityModal = ({ isOpen, onClose, onSave, initialDayIndex, initialSlotIndex }) => {
        const [title, setTitle] = useState('');
        const [department, setDepartment] = useState('');
        const [group, setGroup] = useState('');
        const [location, setLocation] = useState('');

        if (!isOpen) return null;

        const handleSubmit = (e) => {
          e.preventDefault();
          onSave({ title, department, group, location, dayIndex: initialDayIndex, slotIndex: initialSlotIndex });
          setTitle(''); setDepartment(''); setGroup(''); setLocation(''); onClose();
        };

        const slotLabel = TIME_SLOTS.find(s => s.id === initialSlotIndex)?.label;
        const dayLabel = DAYS[initialDayIndex];

        return (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
              <div className="bg-indigo-600 px-6 py-4 flex justify-between items-center">
                <h3 className="text-white font-bold text-lg">Nueva Actividad</h3>
                <button onClick={onClose} className="text-white hover:bg-indigo-700 p-1 rounded-full transition-colors"><X size={20} /></button>
              </div>
              <div className="px-6 py-2 bg-indigo-50 border-b border-indigo-100"><p className="text-sm text-indigo-800 font-medium">{dayLabel} - {slotLabel}</p></div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div><label className="block text-sm font-medium text-gray-700 mb-1">Actividad</label><input required type="text" value={title} onChange={(e) => setTitle(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all" placeholder="Ej: Examen de Matemáticas" /></div>
                <div><label className="block text-sm font-medium text-gray-700 mb-1">Departamento Responsable</label><input required type="text" value={department} onChange={(e) => setDepartment(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all" placeholder="Ej: Matemáticas" /></div>
                <div className="grid grid-cols-2 gap-4">
                  <div><label className="block text-sm font-medium text-gray-700 mb-1">Grupo de Clase</label><input required type="text" value={group} onChange={(e) => setGroup(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all" placeholder="Ej: 2º ESO A" /></div>
                  <div><label className="block text-sm font-medium text-gray-700 mb-1">Lugar</label><input required type="text" value={location} onChange={(e) => setLocation(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all" placeholder="Ej: Aula 204" /></div>
                </div>
                <div className="pt-4 flex justify-end space-x-3">
                  <button type="button" onClick={onClose} className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors">Cancelar</button>
                  <button type="submit" className="px-4 py-2 text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg font-medium shadow-md hover:shadow-lg transition-all">Guardar Actividad</button>
                </div>
              </form>
            </div>
          </div>
        );
      };

      const ExportButton = ({ activities }) => {
        const [isModalOpen, setIsModalOpen] = useState(false);
        const [password, setPassword] = useState('');
        const [error, setError] = useState('');

        const handleConfirm = async () => {
          if (password === '1234') { await generateWordDocument(activities); setIsModalOpen(false); } else { setError('Contraseña incorrecta'); }
        };

        return (
          <>
            <button onClick={() => { setIsModalOpen(true); setPassword(''); setError(''); }} className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-bold shadow-lg transition-all transform hover:scale-105">
              <Download size={20} /> Exportar a Word
            </button>
            {isModalOpen && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
                <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-sm animate-in fade-in zoom-in duration-200">
                  <div className="flex items-center gap-3 mb-4 text-gray-800"><div className="p-2 bg-green-100 rounded-full text-green-600"><Lock size={24} /></div><h3 className="text-xl font-bold">Seguridad</h3></div>
                  <p className="text-gray-600 mb-4">Introduce la contraseña para descargar el cronograma.</p>
                  <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none mb-2" placeholder="Contraseña" autoFocus onKeyDown={(e) => e.key === 'Enter' && handleConfirm()} />
                  {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
                  <div className="flex justify-end gap-2 mt-4">
                    <button onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg font-medium">Cancelar</button>
                    <button onClick={handleConfirm} className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium">Descargar</button>
                  </div>
                </div>
              </div>
            )}
          </>
        );
      };

      const ResetButton = ({ onReset }) => {
        const [isModalOpen, setIsModalOpen] = useState(false);
        const [password, setPassword] = useState('');
        const [error, setError] = useState('');

        const handleConfirm = () => {
          if (password === '1234') { onReset(); setIsModalOpen(false); } else { setError('Contraseña incorrecta'); }
        };

        return (
          <>
            <button onClick={() => { setIsModalOpen(true); setPassword(''); setError(''); }} className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-3 rounded-lg font-bold shadow-lg transition-all transform hover:scale-105" title="Borrar todas las actividades">
              <Trash2 size={20} /> <span className="hidden sm:inline">Borrar Todo</span>
            </button>
            {isModalOpen && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
                <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-sm animate-in fade-in zoom-in duration-200 border-t-4 border-red-500">
                  <div className="flex items-center gap-3 mb-4 text-gray-800"><div className="p-2 bg-red-100 rounded-full text-red-600"><AlertTriangle size={24} /></div><h3 className="text-xl font-bold">Zona de Peligro</h3></div>
                  <p className="text-gray-600 mb-4">Esta acción eliminará <strong>todas</strong> las actividades del calendario. Introduce la contraseña para confirmar.</p>
                  <div className="relative mb-2"><div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400"><Lock size={16} /></div><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none" placeholder="Contraseña" autoFocus onKeyDown={(e) => e.key === 'Enter' && handleConfirm()} /></div>
                  {error && <p className="text-red-500 text-sm mb-2 font-medium">{error}</p>}
                  <div className="flex justify-end gap-2 mt-6">
                    <button onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg font-medium transition-colors">Cancelar</button>
                    <button onClick={handleConfirm} className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium shadow-sm transition-colors">Confirmar Borrado</button>
                  </div>
                </div>
              </div>
            )}
          </>
        );
      };

      // --- MAIN APP ---
      const App = () => {
        const [activities, setActivities] = useState([]);
        const [isLoading, setIsLoading] = useState(true);
        const [isSaving, setIsSaving] = useState(false);
        const [isModalOpen, setIsModalOpen] = useState(false);
        const [selectedSlot, setSelectedSlot] = useState(null);

        // Cargar datos al inicio
        useEffect(() => {
          const init = async () => {
            const data = await storageService.load();
            setActivities(data);
            setIsLoading(false);
          };
          init();
        }, []);

        const handleAddClick = (dayIndex, slotIndex) => {
          setSelectedSlot({ day: dayIndex, slot: slotIndex });
          setIsModalOpen(true);
        };

        const handleSaveActivity = async (newActivity) => {
          const activity = { ...newActivity, id: crypto.randomUUID() };
          const updatedActivities = [...activities, activity];
          setActivities(updatedActivities);
          
          setIsSaving(true);
          await storageService.save(updatedActivities);
          setIsSaving(false);
        };

        const handleResetActivities = async () => {
          setActivities([]);
          setIsSaving(true);
          await storageService.save([]);
          setIsSaving(false);
        };

        const getActivitiesForCell = (dayIndex, slotIndex) => activities.filter(a => a.dayIndex === dayIndex && a.slotIndex === slotIndex);

        if (isLoading) {
          return (
            <div className="min-h-screen flex items-center justify-center bg-gray-100">
              <div className="flex flex-col items-center gap-4">
                <Loader2 className="animate-spin text-indigo-600" size={48} />
                <p className="text-gray-600 font-medium">Cargando calendario...</p>
              </div>
            </div>
          );
        }

        return (
          <div className="min-h-screen bg-gray-100 flex flex-col">
            <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-30">
              <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="bg-indigo-600 p-2 rounded-lg text-white"><CalendarIcon size={28} /></div>
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900 leading-none">Semana Escolar</h1>
                    <div className="flex items-center gap-2 mt-1">
                      <p className="text-sm text-gray-500 font-medium">23 - 27 de Marzo</p>
                      {CLOUD_CONFIG.enabled ? (
                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full flex items-center gap-1">
                          {isSaving ? <Loader2 size={10} className="animate-spin" /> : <Cloud size={10} />}
                          {isSaving ? 'Guardando...' : 'Sincronizado en Nube'}
                        </span>
                      ) : (
                        <span className="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full flex items-center gap-1">
                          <CloudOff size={10} /> Modo Local
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <ResetButton onReset={handleResetActivities} />
                  <ExportButton activities={activities} />
                </div>
              </div>
            </header>

            <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-auto">
              <div className="max-w-8xl mx-auto bg-white rounded-xl shadow-xl overflow-hidden border border-gray-200">
                <div className="overflow-x-auto">
                  <div className="min-w-[1200px]">
                    <div className="grid grid-cols-[120px_repeat(5,1fr)] border-b-2 border-gray-200 bg-gray-50">
                      <div className="p-4 font-bold text-gray-400 text-center flex items-center justify-center border-r border-gray-200">HORA</div>
                      {DAYS.map((day, index) => (
                        <div key={index} className="p-4 font-bold text-indigo-900 text-center text-lg border-r border-gray-200 last:border-r-0">{day}</div>
                      ))}
                    </div>

                    {TIME_SLOTS.map((slot) => {
                      const isRecess = slot.isRecess;
                      if (isRecess) {
                        return (
                          <div key={slot.id} className="grid grid-cols-[120px_1fr] bg-amber-50 border-b border-gray-200">
                            <div className="p-4 flex flex-col justify-center items-center text-center border-r border-gray-200 bg-amber-100 text-amber-800">
                              <span className="font-bold text-sm">{slot.label}</span>
                              <span className="text-xs opacity-75">{slot.time}</span>
                            </div>
                            <div className="p-4 flex items-center justify-center text-amber-700 font-bold tracking-widest text-xl">RECREO</div>
                          </div>
                        );
                      }

                      return (
                        <div key={slot.id} className="grid grid-cols-[120px_repeat(5,1fr)] border-b border-gray-200 last:border-b-0 min-h-[160px]">
                          <div className="p-4 flex flex-col justify-center items-center text-center border-r border-gray-200 bg-gray-50">
                            <span className="font-bold text-gray-700">{slot.label}</span>
                            <span className="text-xs text-gray-500 mt-1">{slot.time}</span>
                          </div>
                          {DAYS.map((_, dayIndex) => {
                            const cellActivities = getActivitiesForCell(dayIndex, slot.id);
                            return (
                              <div key={dayIndex} className="relative p-2 border-r border-gray-200 last:border-r-0 group hover:bg-gray-50 transition-colors">
                                <div className="space-y-2 mb-8">
                                  {cellActivities.map((act) => (
                                    <div key={act.id} className="bg-white border-l-4 border-indigo-500 shadow-sm rounded p-2 text-sm hover:shadow-md transition-shadow">
                                      <div className="font-bold text-gray-900 mb-1">{act.title}</div>
                                      <div className="space-y-0.5 text-xs text-gray-600">
                                        <div className="flex items-center gap-1"><Building2 size={12} className="text-indigo-400" /><span>{act.department}</span></div>
                                        <div className="flex items-center gap-1"><Users size={12} className="text-indigo-400" /><span>{act.group}</span></div>
                                        <div className="flex items-center gap-1"><MapPin size={12} className="text-indigo-400" /><span>{act.location}</span></div>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                                <button onClick={() => handleAddClick(dayIndex, slot.id)} className={`absolute bottom-2 right-2 p-1.5 rounded-full bg-indigo-100 text-indigo-600 hover:bg-indigo-600 hover:text-white transition-all ${cellActivities.length === 0 ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`} title="Añadir actividad">
                                  <Plus size={20} />
                                </button>
                              </div>
                            );
                          })}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </main>

            {selectedSlot && (
              <ActivityModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={handleSaveActivity}
                initialDayIndex={selectedSlot.day}
                initialSlotIndex={selectedSlot.slot}
              />
            )}
          </div>
        );
      };

      const root = ReactDOM.createRoot(document.getElementById('root'));
      root.render(<App />);
    </script>
  </body>
</html>
"""

# Renderizar el componente HTML en Streamlit
components.html(html_code.replace("__CLOUD_CONFIG__", cloud_config), height=1000, scrolling=True)
