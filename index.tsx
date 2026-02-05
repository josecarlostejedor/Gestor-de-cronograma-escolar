import React, { useState, useEffect, useCallback } from 'react';
import { createRoot } from 'react-dom/client';
import { 
  Plus, 
  FileText, 
  Lock, 
  Calendar as CalendarIcon, 
  Trash2, 
  Cloud,
  User,
  MapPin,
  Users,
  Clock,
  ChevronRight,
  X
} from 'lucide-react';

const CLOUD_URL = 'https://api.keyvalue.xyz/0f8c2e4a/ies-lucia-medrano-v100';
const PASSWORD_SECRET = '1234';

const TIME_SLOTS = [
  { id: '1h', label: '1ª hora', timeRange: '8:50 - 9:45' },
  { id: '2h', label: '2ª hora', timeRange: '9:45 - 10:40' },
  { id: '3h', label: '3ª hora', timeRange: '10:40 - 11:30' },
  { id: 'recreo', label: 'Recreo', timeRange: '11:30 - 12:00' },
  { id: '4h', label: '4ª hora', timeRange: '12:00 - 12:55' },
  { id: '5h', label: '5ª hora', timeRange: '12:55 - 13:45' },
  { id: '6h', label: '6ª hora', timeRange: '13:45 - 14:35' },
];

const DAYS = [
  { date: '23/03', dayName: 'Lunes' },
  { date: '24/03', dayName: 'Martes' },
  { date: '25/03', dayName: 'Miércoles' },
  { date: '26/03', dayName: 'Jueves' },
  { date: '27/03', dayName: 'Viernes' },
];

const App = () => {
  const [schedule, setSchedule] = useState<any>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeSlot, setActiveSlot] = useState<any>(null);
  const [authModal, setAuthModal] = useState<any>({ open: false, action: null });
  const [password, setPassword] = useState('');
  const [formData, setFormData] = useState({
    actividad: '', profesor: '', departamento: '', grupo: '', lugar: ''
  });

  const syncFromCloud = useCallback(async (isInitial = false) => {
    if (isInitial) setIsLoading(true);
    setIsSyncing(true);
    try {
      const response = await fetch(CLOUD_URL);
      if (response.ok) {
        const data = await response.json();
        if (data && typeof data === 'object') setSchedule(data);
      }
    } catch (error) {
      console.warn("Base de datos nueva.");
    } finally {
      setIsLoading(false);
      setIsSyncing(false);
    }
  }, []);

  const saveToCloud = async (newSchedule: any) => {
    setIsSyncing(true);
    try {
      await fetch(CLOUD_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSchedule)
      });
    } catch (error) {
      console.error("Error sincronizando:", error);
    } finally {
      setIsSyncing(false);
    }
  };

  useEffect(() => {
    syncFromCloud(true);
    const interval = setInterval(() => {
      if (!isModalOpen && !authModal.open) syncFromCloud();
    }, 15000);
    return () => clearInterval(interval);
  }, [syncFromCloud, isModalOpen, authModal.open]);

  const handleAdd = async () => {
    if (!formData.actividad.trim() || !activeSlot) return;
    const newSchedule = { ...schedule };
    if (!newSchedule[activeSlot.day]) newSchedule[activeSlot.day] = {};
    if (!newSchedule[activeSlot.day][activeSlot.id]) newSchedule[activeSlot.day][activeSlot.id] = [];
    
    newSchedule[activeSlot.day][activeSlot.id].push({
      ...formData,
      id: Date.now().toString()
    });

    setSchedule(newSchedule);
    await saveToCloud(newSchedule);
    setIsModalOpen(false);
    setFormData({ actividad: '', profesor: '', departamento: '', grupo: '', lugar: '' });
  };

  const handleExport = async () => {
    const docxLib = (window as any).docx;
    if (!docxLib) return alert("Cargando motor de Word...");

    const { Document, Packer, Paragraph, Table, TableCell, TableRow, WidthType, AlignmentType, PageOrientation, TextRun, HeadingLevel } = docxLib;
    
    const tableRows = [
      new TableRow({
        children: [
          new TableCell({ children: [new Paragraph({ text: "HORA", alignment: AlignmentType.CENTER })], shading: { fill: "1e293b" } }),
          ...DAYS.map(d => new TableCell({ 
            children: [new Paragraph({ children: [new TextRun({ text: d.dayName.toUpperCase(), bold: true, color: "FFFFFF" })], alignment: AlignmentType.CENTER })], 
            shading: { fill: "1e293b" } 
          }))
        ]
      })
    ];

    TIME_SLOTS.forEach(slot => {
      const cells = [
        new TableCell({
          children: [new Paragraph({ text: slot.label, alignment: AlignmentType.CENTER }), new Paragraph({ text: slot.timeRange, alignment: AlignmentType.CENTER })],
          shading: { fill: slot.id === 'recreo' ? "f1f5f9" : "ffffff" }
        })
      ];
      DAYS.forEach(day => {
        const acts = schedule[day.dayName]?.[slot.id] || [];
        const content = acts.flatMap((a: any) => [
          new Paragraph({ children: [new TextRun({ text: a.actividad.toUpperCase(), bold: true, size: 18 })] }),
          new Paragraph({ children: [new TextRun({ text: `Prof: ${a.profesor}`, size: 16 })] }),
          new Paragraph({ children: [new TextRun({ text: `${a.grupo} - ${a.lugar}`, size: 14, color: "666666" })], spacing: { after: 150 } })
        ]);
        cells.push(new TableCell({ children: content.length > 0 ? content : [new Paragraph("")] }));
      });
      tableRows.push(new TableRow({ children: cells }));
    });

    const doc = new Document({
      sections: [{
        properties: { page: { size: { orientation: PageOrientation.LANDSCAPE } } },
        children: [
          new Paragraph({ text: "IES LUCÍA DE MEDRANO - SEMANA CULTURAL MARZO", heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER, spacing: { after: 400 } }),
          new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: tableRows })
        ]
      }]
    });

    const blob = await Packer.toBlob(doc);
    (window as any).saveAs(blob, "Semana_Cultural_IES_Lucia_Medrano.docx");
  };

  const handleAuth = () => {
    if (password === PASSWORD_SECRET) {
      if (authModal.action === 'export') handleExport();
      if (authModal.action === 'clear') {
        setSchedule({});
        saveToCloud({});
      }
      setAuthModal({ open: false, action: null });
      setPassword('');
    } else {
      alert("Acceso denegado");
    }
  };

  if (isLoading) return (
    <div className="min-h-screen bg-indigo-700 flex items-center justify-center text-white">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4"></div>
        <p className="font-bold text-xs uppercase tracking-widest">Sincronizando IES Lucía de Medrano</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <header className="bg-white border-b sticky top-0 z-40 p-4 md:px-10 flex flex-col md:flex-row justify-between items-center gap-4 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="bg-indigo-600 text-white p-3 rounded-2xl shadow-lg"><CalendarIcon /></div>
          <div>
            <h1 className="text-xl font-black text-slate-900 tracking-tight">Semana Cultural</h1>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Servicio en vivo • 23-27 Marzo</span>
              {isSyncing && <Cloud size={14} className="text-indigo-500 animate-bounce ml-2" />}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setAuthModal({ open: true, action: 'clear' })} className="p-2 text-slate-300 hover:text-red-500 transition-colors"><Trash2 size={20} /></button>
          <button onClick={() => setAuthModal({ open: true, action: 'export' })} className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-xl font-black text-xs shadow-lg transition-all flex items-center gap-2">
            <FileText size={16} /> EXPORTAR WORD
          </button>
        </div>
      </header>

      <main className="flex-1 p-4 md:p-8 overflow-x-auto custom-scrollbar">
        <div className="bg-white border rounded-[3rem] shadow-2xl overflow-hidden min-w-[1250px]">
          <table className="w-full border-collapse table-fixed">
            <thead>
              <tr className="bg-slate-900 text-white">
                <th className="w-44 p-6 text-[10px] font-black uppercase opacity-40 text-center tracking-widest">Horario</th>
                {DAYS.map(day => (
                  <th key={day.dayName} className="p-6 text-left border-l border-white/5">
                    <div className="text-2xl font-black">{day.dayName}</div>
                    <div className="text-[10px] font-bold text-indigo-400 uppercase mt-1">{day.date}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {TIME_SLOTS.map(slot => (
                <tr key={slot.id} className={slot.id === 'recreo' ? 'recreo-row' : ''}>
                  <td className="p-6 border-b border-slate-100 text-center border-r border-slate-50 bg-slate-50/20">
                    <div className="font-black text-xs text-slate-900 uppercase tracking-tighter">{slot.label}</div>
                    <div className="text-[10px] font-bold text-indigo-600 mt-2 flex items-center justify-center gap-1.5">
                      <Clock size={12} /> {slot.timeRange}
                    </div>
                  </td>
                  {DAYS.map(day => {
                    const acts = schedule[day.dayName]?.[slot.id] || [];
                    return (
                      <td key={day.dayName + slot.id} className="p-3 border-b border-slate-100 align-top">
                        <div className="space-y-3 mb-3">
                          {acts.map((a: any) => (
                            <div key={a.id} className="bg-white border border-slate-200 border-l-[6px] border-l-indigo-600 p-4 rounded-2xl shadow-sm hover:shadow-xl transition-all">
                              <div className="font-black text-xs text-slate-900 leading-tight uppercase mb-3">{a.actividad}</div>
                              <div className="flex items-center gap-1.5 text-[10px] font-bold text-indigo-700 bg-indigo-50 p-2 rounded-xl mb-3">
                                <User size={12} /> {a.profesor}
                              </div>
                              <div className="grid grid-cols-2 gap-2 text-[9px] font-bold text-slate-400 uppercase pl-1">
                                <div className="flex items-center gap-1.5"><Users size={12}/> {a.grupo}</div>
                                <div className="flex items-center gap-1.5"><MapPin size={12}/> {a.lugar}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                        <button 
                          onClick={() => { setActiveSlot({ day: day.dayName, id: slot.id, label: slot.label }); setIsModalOpen(true); }}
                          className="w-full py-5 border-2 border-dashed border-slate-100 rounded-2xl text-slate-300 hover:border-indigo-400 hover:text-indigo-600 hover:bg-indigo-50 transition-all flex flex-col items-center justify-center gap-2"
                        >
                          <Plus size={24} className="opacity-40" />
                          <span className="text-[9px] font-black uppercase tracking-widest">Añadir</span>
                        </button>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>

      {isModalOpen && activeSlot && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-[2.5rem] shadow-2xl w-full max-w-lg overflow-hidden">
            <div className="bg-indigo-600 p-10 text-white text-center relative">
              <button onClick={() => setIsModalOpen(false)} className="absolute top-6 right-6 text-white/40 hover:text-white"><X /></button>
              <h2 className="text-3xl font-black tracking-tighter uppercase">Programar</h2>
              <p className="text-[10px] font-bold uppercase tracking-widest opacity-60 mt-2">{activeSlot.day} • {activeSlot.label}</p>
            </div>
            <div className="p-10 space-y-4">
              <input autoFocus placeholder="Nombre de la Actividad" className="w-full p-5 bg-slate-50 border-2 border-transparent rounded-2xl focus:border-indigo-600 outline-none text-sm font-bold transition-all" value={formData.actividad} onChange={e=>setFormData({...formData, actividad: e.target.value})} />
              <input placeholder="Profesor/a Responsable" className="w-full p-5 bg-slate-50 border-2 border-transparent rounded-2xl focus:border-indigo-600 outline-none text-sm font-bold transition-all" value={formData.profesor} onChange={e=>setFormData({...formData, profesor: e.target.value})} />
              <div className="grid grid-cols-2 gap-4">
                <input placeholder="Dpto." className="w-full p-5 bg-slate-50 border-2 border-transparent rounded-2xl focus:border-indigo-600 outline-none text-sm font-bold transition-all" value={formData.departamento} onChange={e=>setFormData({...formData, departamento: e.target.value})} />
                <input placeholder="Grupo" className="w-full p-5 bg-slate-50 border-2 border-transparent rounded-2xl focus:border-indigo-600 outline-none text-sm font-bold transition-all" value={formData.grupo} onChange={e=>setFormData({...formData, grupo: e.target.value})} />
              </div>
              <input placeholder="Lugar o Aula" className="w-full p-5 bg-slate-50 border-2 border-transparent rounded-2xl focus:border-indigo-600 outline-none text-sm font-bold transition-all" value={formData.lugar} onChange={e=>setFormData({...formData, lugar: e.target.value})} />
              <button onClick={handleAdd} className="w-full py-5 bg-indigo-600 text-white font-black rounded-2xl shadow-xl hover:bg-indigo-700 transition-all uppercase text-xs tracking-widest mt-6">Publicar Actividad</button>
            </div>
          </div>
        </div>
      )}

      {authModal.open && (
        <div className="fixed inset-0 bg-slate-900/95 backdrop-blur-2xl z-[100] flex items-center justify-center p-4">
          <div className="bg-white p-12 rounded-[4rem] w-full max-w-sm text-center shadow-2xl">
            <div className="bg-indigo-50 text-indigo-600 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-8"><Lock size={32} /></div>
            <h3 className="text-3xl font-black text-slate-800 mb-2">Seguridad</h3>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-10">Clave: 1234</p>
            <input 
              type="password" 
              autoFocus 
              className="w-full p-6 bg-slate-50 border-2 border-transparent rounded-[2rem] focus:border-indigo-600 outline-none text-center text-4xl font-black tracking-[0.5em] mb-10"
              value={password} 
              onChange={e => setPassword(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleAuth()}
            />
            <div className="flex flex-col gap-4">
              <button onClick={handleAuth} className="w-full py-6 bg-indigo-600 text-white font-black rounded-[2rem] shadow-xl uppercase text-xs tracking-widest">Validar Acceso</button>
              <button onClick={() => setAuthModal({open: false, action: null})} className="w-full py-2 text-slate-300 font-bold hover:text-slate-500 uppercase text-[10px]">Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const rootElement = document.getElementById('root');
if (rootElement) {
  createRoot(rootElement).render(<App />);
}