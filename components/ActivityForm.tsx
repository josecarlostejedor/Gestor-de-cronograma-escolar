
import React, { useState } from 'react';
import { Activity } from '../types';

interface ActivityFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (activity: Omit<Activity, 'id'>) => void;
  dayName: string;
  slotLabel: string;
}

const ActivityForm: React.FC<ActivityFormProps> = ({ isOpen, onClose, onSubmit, dayName, slotLabel }) => {
  const [formData, setFormData] = useState({
    actividad: '',
    departamento: '',
    profesor: '',
    grupo: '',
    lugar: ''
  });

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
    setFormData({ actividad: '', departamento: '', profesor: '', grupo: '', lugar: '' });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden transform transition-all border border-slate-200">
        <div className="bg-indigo-700 p-6 text-white">
          <h3 className="text-xl font-bold">Nueva Actividad Semana Cultural</h3>
          <p className="text-sm opacity-80 mt-1">{dayName} • {slotLabel}</p>
        </div>
        
        <form onSubmit={handleSubmit} className="p-8 space-y-5">
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Nombre de la Actividad</label>
            <input
              required
              autoFocus
              className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-3 border transition-all"
              value={formData.actividad}
              onChange={(e) => setFormData({...formData, actividad: e.target.value})}
              placeholder="Ej: Concierto de Primavera"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Profesor Responsable</label>
              <input
                required
                className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-3 border transition-all"
                value={formData.profesor}
                onChange={(e) => setFormData({...formData, profesor: e.target.value})}
                placeholder="Nombre del docente"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Departamento</label>
              <input
                required
                className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-3 border transition-all"
                value={formData.departamento}
                onChange={(e) => setFormData({...formData, departamento: e.target.value})}
                placeholder="Ej: Música"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Grupo de Clase</label>
              <input
                required
                className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-3 border transition-all"
                value={formData.grupo}
                onChange={(e) => setFormData({...formData, grupo: e.target.value})}
                placeholder="Ej: Todos / 1º Bach"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Lugar</label>
              <input
                required
                className="block w-full rounded-xl border-slate-200 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-3 border transition-all"
                value={formData.lugar}
                onChange={(e) => setFormData({...formData, lugar: e.target.value})}
                placeholder="Ej: Salón de Actos"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-6 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 text-sm font-semibold text-slate-600 bg-slate-100 rounded-xl hover:bg-slate-200 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-5 py-2.5 text-sm font-semibold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 shadow-lg shadow-indigo-200 transition-all active:scale-95"
            >
              Añadir al Horario
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ActivityForm;
