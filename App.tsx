
import React, { useState, useEffect } from 'react';
import { Plus, FileText, Lock, Calendar as CalendarIcon, Clock, Trash2, ShieldAlert, Download } from 'lucide-react';
import { TIME_SLOTS, DAYS, PASSWORD_EXPORT } from './constants';
import { ScheduleData, Activity, DayOfWeek } from './types';
import { exportToWord } from './services/wordExport';
import ActivityForm from './components/ActivityForm';

// Fallback simple para IDs si crypto.randomUUID no está disponible en el iframe
const generateId = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).substring(2, 15);
};

const App: React.FC = () => {
  const [schedule, setSchedule] = useState<ScheduleData>(() => {
    try {
      const saved = localStorage.getItem('ies-lucia-medrano-schedule');
      return saved ? JSON.parse(saved) : {};
    } catch (e) {
      return {};
    }
  });

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeSlot, setActiveSlot] = useState<{ day: DayOfWeek; slotId: string; label: string } | null>(null);
  
  const [authAction, setAuthAction] = useState<'export' | 'clear' | null>(null);
  const [passwordInput, setPasswordInput] = useState('');
  const [passwordError, setPasswordError] = useState(false);

  useEffect(() => {
    if (Object.keys(schedule).length === 0) {
       localStorage.removeItem('ies-lucia-medrano-schedule');
    } else {
       localStorage.setItem('ies-lucia-medrano-schedule', JSON.stringify(schedule));
    }
  }, [schedule]);

  const handleAddActivity = (data: Omit<Activity, 'id'>) => {
    if (!activeSlot) return;

    const newActivity: Activity = {
      ...data,
      id: generateId()
    };

    setSchedule(prev => {
      const dayData = prev[activeSlot.day] || {};
      const slotActivities = dayData[activeSlot.slotId] || [];
      return {
        ...prev,
        [activeSlot.day]: {
          ...dayData,
          [activeSlot.slotId]: [...slotActivities, newActivity]
        }
      };
    });
  };

  const openForm = (day: DayOfWeek, slotId: string, label: string) => {
    setActiveSlot({ day, slotId, label });
    setIsModalOpen(true);
  };

  const executeAuthAction = () => {
    if (passwordInput === PASSWORD_EXPORT) {
      if (authAction === 'export') {
        exportToWord(schedule);
      } else if (authAction === 'clear') {
        localStorage.clear();
        setSchedule({});
      }
      setAuthAction(null);
      setPasswordInput('');
      setPasswordError(false);
    } else {
      setPasswordError(true);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-20">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40 px-4 py-4 md:px-8 shadow-sm">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-700 text-white rounded-2xl shadow-lg shadow-indigo-100">
              <CalendarIcon size={32} />
            </div>
            <div>
              <h1 className="text-xl md:text-2xl font-black text-slate-800 tracking-tight leading-tight">
                Semana Cultural IES Lucía de Medrano
              </h1>
              <p className="text-sm font-semibold text-indigo-600">Planificador de Actividades (23-27 Marzo)</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setAuthAction('clear')}
              className="flex items-center justify-center gap-2 bg-white border-2 border-red-100 hover:bg-red-50 text-red-600 px-5 py-2.5 rounded-xl font-bold transition-all active:scale-95"
            >
              <Trash2 size={18} />
              Borrar Todo
            </button>
            <button
              onClick={() => setAuthAction('export')}
              className="flex items-center justify-center gap-2 bg-indigo-700 hover:bg-indigo-800 text-white px-6 py-2.5 rounded-xl font-bold transition-all shadow-md active:scale-95"
            >
              <FileText size={20} />
              Exportar Word
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-[1500px] mx-auto p-4 md:p-8">
        <div className="overflow-x-auto rounded-3xl border border-slate-200 bg-white shadow-2xl">
          <table className="w-full border-collapse min-w-[1200px]">
            <thead>
              <tr className="bg-slate-800 text-white">
                <th className="p-5 border-b border-slate-700 w-40 sticky left-0 z-20 bg-slate-800">
                  <div className="flex items-center justify-center gap-2 text-slate-400 font-bold uppercase text-xs tracking-widest">
                    <Clock size={16} />
                    Horario
                  </div>
                </th>
                {DAYS.map(day => (
                  <th key={day.dayName} className="p-6 border-b border-slate-700 min-w-[220px]">
                    <div className="text-white font-black text-xl tracking-tight">{day.dayName}</div>
                    <div className="text-slate-400 font-bold text-sm mt-1">{day.date}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {TIME_SLOTS.map(slot => (
                <tr key={slot.id} className={slot.id === 'recreo' ? 'bg-indigo-50/40' : 'hover:bg-slate-50 transition-colors'}>
                  <td className="p-5 border-b border-r border-slate-100 font-medium sticky left-0 z-20 bg-white shadow-[2px_0_5px_rgba(0,0,0,0.02)]">
                    <div className="text-slate-900 text-base font-black text-center">{slot.label}</div>
                    <div className="text-indigo-500 text-xs mt-1 font-bold text-center bg-indigo-50 rounded-full py-1">{slot.timeRange}</div>
                  </td>
                  {DAYS.map(day => {
                    const activities = schedule[day.dayName]?.[slot.id] || [];
                    const isMarked = activities.length > 0;
                    
                    return (
                      <td key={`${day.dayName}-${slot.id}`} className="p-4 border-b border-slate-100 align-top group">
                        <div className="space-y-3 mb-3">
                          {activities.map(act => (
                            <div key={act.id} className="bg-white border-l-4 border-l-indigo-600 border border-slate-200 p-4 rounded-xl text-sm shadow-sm hover:shadow-md transition-all relative">
                              <div className="font-bold text-slate-800 text-base leading-tight mb-2">{act.actividad}</div>
                              <div className="space-y-1">
                                <p className="text-indigo-700 font-bold text-xs">Prof: {act.profesor}</p>
                                <p className="text-slate-500 text-xs font-medium bg-slate-100 px-2 py-0.5 rounded inline-block mr-1">{act.departamento}</p>
                                <p className="text-slate-500 text-xs font-medium bg-slate-100 px-2 py-0.5 rounded inline-block">{act.lugar}</p>
                                <div className="mt-1 text-[10px] font-black text-indigo-400 uppercase tracking-widest">{act.grupo}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                        <button
                          onClick={() => openForm(day.dayName, slot.id, `${slot.label} (${slot.timeRange})`)}
                          className={`w-full py-3 flex items-center justify-center gap-2 border-2 border-dashed rounded-xl transition-all ${
                            isMarked 
                            ? 'border-indigo-100 text-indigo-300 hover:border-indigo-300 hover:text-indigo-600' 
                            : 'border-slate-100 text-slate-300 hover:border-indigo-200 hover:text-indigo-500'
                          }`}
                        >
                          <Plus size={20} />
                          <span className="text-xs font-bold uppercase tracking-wider">Añadir</span>
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

      {authAction && (
        <div className="fixed inset-0 bg-slate-900/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-sm overflow-hidden p-10 border border-slate-100">
            <div className="flex justify-center mb-6">
              <div className={`p-5 rounded-3xl ${authAction === 'clear' ? 'bg-red-100 text-red-600' : 'bg-indigo-100 text-indigo-600'}`}>
                {authAction === 'clear' ? <ShieldAlert size={40} /> : <Lock size={40} />}
              </div>
            </div>
            <h3 className="text-2xl font-black text-center mb-2 text-slate-800">Acceso Protegido</h3>
            <p className="text-slate-500 text-center text-sm mb-8 leading-relaxed">
              Introduce la clave 1234 para confirmar la acción.
            </p>
            
            <input
              type="password"
              className="w-full p-4 border-2 border-slate-100 rounded-2xl text-center text-2xl font-bold focus:ring-4 focus:ring-indigo-100 transition-all tracking-widest outline-none"
              placeholder="••••"
              value={passwordInput}
              onChange={(e) => { setPasswordInput(e.target.value); setPasswordError(false); }}
              onKeyDown={(e) => e.key === 'Enter' && executeAuthAction()}
              autoFocus
            />
            {passwordError && <p className="text-red-500 text-xs mt-3 text-center font-bold">Contraseña incorrecta</p>}

            <div className="flex flex-col gap-4 mt-10">
              <button
                onClick={executeAuthAction}
                className={`w-full font-black py-4 rounded-2xl text-white shadow-xl active:scale-95 transition-all ${
                  authAction === 'clear' ? 'bg-red-600 hover:bg-red-700 shadow-red-100' : 'bg-indigo-700 hover:bg-indigo-800 shadow-indigo-100'
                }`}
              >
                Confirmar
              </button>
              <button
                onClick={() => { setAuthAction(null); setPasswordInput(''); setPasswordError(false); }}
                className="w-full text-slate-400 font-bold py-2 hover:text-slate-600 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      <ActivityForm
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleAddActivity}
        dayName={activeSlot?.day || ''}
        slotLabel={activeSlot?.label || ''}
      />
    </div>
  );
};

export default App;