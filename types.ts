
export interface Activity {
  id: string;
  actividad: string;
  departamento: string;
  profesor: string; // Nuevo campo
  grupo: string;
  lugar: string;
}

export interface TimeSlot {
  id: string;
  label: string;
  timeRange: string;
}

export type DayOfWeek = 'Lunes' | 'Martes' | 'Miércoles' | 'Jueves' | 'Viernes';

export interface DayData {
  date: string;
  dayName: DayOfWeek;
}

export type ScheduleData = Record<string, Record<string, Activity[]>>;
