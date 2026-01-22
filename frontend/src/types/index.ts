// Severity levels for osteoarthritis
export type SeverityLevel = 'Normal' | 'Doubtful' | 'Mild' | 'Moderate' | 'Severe';

// Patient information (matches hospitalDB.patients)
export interface Patient {
    patientId: string;
    age: number;
    whatsappNumber: string;
    severity: string;
    pastHistory: string;
}

// User information (matches hospitalDB.users)
export interface User {
    username: string;
    patientId: string;
}

// Diet recommendation structure
export interface DietRecommendation {
    category: string;
    category_kn?: string;
    items: string[];
    items_kn?: string[];
    frequency: string;
    frequency_kn?: string;
}

// Exercise plan structure
export interface ExercisePlan {
    name: string;
    name_kn?: string;
    duration: string;
    duration_kn?: string;
    frequency: string;
    frequency_kn?: string;
    intensity: string;
    intensity_kn?: string;
    tips: string;
    tips_kn?: string;
}

// Alert/Reminder structure
export interface Alert {
    type: 'exercise' | 'medication' | 'meal' | 'checkup' | 'hydration' | 'reminder';
    title: string;
    title_kn?: string;
    description: string;
    description_kn?: string;
    time: string;
    frequency: 'once' | 'daily' | 'weekly' | 'monthly' | string;
    frequency_kn?: string;
}

// Calendar Event (extends Alert with additional metadata)
export interface CalendarEvent extends Alert {
    eventId: string;
    isAiGenerated: boolean;
    isModified: boolean;
}

// Analysis result from backend
export interface AnalysisResult {
    severity: SeverityLevel;
    confidence: string;
    diet: DietRecommendation[];
    exercise: ExercisePlan[];
    alerts: Alert[];
    source: 'ai' | 'static';
    disclaimer: string;
}

// Auth data
export interface SignupData {
    whatsappNumber: string;
    username: string;
    password: string;
    age: number;
    pastHistory?: string;
}

export interface LoginData {
    username: string;
    password: string;
}

export interface AuthResponse {
    message: string;
    patient: Patient;
    user?: User;
    otp?: string;
}

// Alert type configuration
export interface AlertTypeConfig {
    type: Alert['type'];
    icon: string;
    label: string;
}

export const ALERT_TYPES: AlertTypeConfig[] = [
    { type: 'exercise', icon: '🏃', label: 'Exercise' },
    { type: 'medication', icon: '💊', label: 'Medication' },
    { type: 'meal', icon: '🥗', label: 'Meal' },
    { type: 'checkup', icon: '🏥', label: 'Checkup' },
    { type: 'hydration', icon: '💧', label: 'Hydration' },
    { type: 'reminder', icon: '🔔', label: 'Reminder' },
];

// Severity configuration
export interface SeverityConfig {
    level: SeverityLevel;
    color: string;
    percent: number;
}

export const SEVERITY_LEVELS: SeverityConfig[] = [
    { level: 'Normal', color: '#10b981', percent: 20 },
    { level: 'Doubtful', color: '#3b82f6', percent: 40 },
    { level: 'Mild', color: '#f59e0b', percent: 60 },
    { level: 'Moderate', color: '#f97316', percent: 80 },
    { level: 'Severe', color: '#ef4444', percent: 100 },
];
