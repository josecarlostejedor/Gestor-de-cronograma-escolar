
import { TimeSlot, DayData } from './types';

export const TIME_SLOTS: TimeSlot[] = [
  { id: '1h', label: '1ª hora', timeRange: '8:50 - 9:45' },
  { id: '2h', label: '2ª hora', timeRange: '9:45 - 10:40' },
  { id: '3h', label: '3ª hora', timeRange: '10:40 - 11:30' },
  { id: 'recreo', label: 'Recreo', timeRange: '11:30 - 11:55' },
  { id: '4h', label: '4ª hora', timeRange: '11:55 - 12:50' },
  { id: '5h', label: '5ª hora', timeRange: '12:50 - 13:45' },
  { id: '6h', label: '6ª hora', timeRange: '13:45 - 14:35' },
];

export const DAYS: DayData[] = [
  { date: '23/03', dayName: 'Lunes' },
  { date: '24/03', dayName: 'Martes' },
  { date: '25/03', dayName: 'Miércoles' },
  { date: '26/03', dayName: 'Jueves' },
  { date: '27/03', dayName: 'Viernes' },
];

export const PASSWORD_EXPORT = '1234';
