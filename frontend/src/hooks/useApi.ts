import { useState, useCallback } from 'react';
import type { AnalysisResult, Patient, SignupData, AuthResponse } from '../types';

interface LoginData {
    username: string;
    password: string;
}

const API_BASE = 'http://127.0.0.1:5000';

export function useApi() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // ===== Signup =====
    const signup = useCallback(async (data: SignupData): Promise<AuthResponse | null> => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE}/api/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Signup failed');
            }

            return result as AuthResponse;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    // ===== Login with password =====
    const login = useCallback(async (data: LoginData): Promise<AuthResponse | null> => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Login failed');
            }

            return result as AuthResponse;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    // ===== Send OTP =====
    const sendOtp = useCallback(async (whatsappNumber: string): Promise<{ otp?: string } | null> => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE}/api/auth/send-otp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ whatsappNumber }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to send OTP');
            }

            return result;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    // ===== Verify OTP =====
    const verifyOtp = useCallback(async (whatsappNumber: string, otp: string): Promise<AuthResponse | null> => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_BASE}/api/auth/verify-otp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ whatsappNumber, otp }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Invalid OTP');
            }

            return result as AuthResponse;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    // ===== Analysis =====
    const analyzeImage = useCallback(async (file: File, patientId: string): Promise<AnalysisResult | null> => {
        setLoading(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('image', file);
            formData.append('patient_id', patientId);

            const response = await fetch(`${API_BASE}/analyze-upload`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Analysis failed');
            }

            const data = await response.json();
            return data as AnalysisResult;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    // ===== Get Patient =====
    const getPatient = useCallback(async (patientId: string): Promise<Patient | null> => {
        try {
            const response = await fetch(`${API_BASE}/api/patient/${patientId}`);
            if (!response.ok) throw new Error('Patient not found');
            const data = await response.json();
            return data.patient;
        } catch (err) {
            console.error('Error fetching patient:', err);
            return null;
        }
    }, []);

    // ===== Calendar APIs =====

    const getCalendar = useCallback(async (patientId: string) => {
        try {
            const response = await fetch(`${API_BASE}/api/calendar/${patientId}`);
            if (!response.ok) throw new Error('Failed to get calendar');
            return await response.json();
        } catch (err) {
            console.error('Error fetching calendar:', err);
            return null;
        }
    }, []);

    const generateCalendar = useCallback(async (patientId: string) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/api/calendar/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ patient_id: patientId }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Failed to generate calendar');
            }

            return await response.json();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    const addCalendarEvent = useCallback(async (patientId: string, event: any) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/api/calendar/event`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ patient_id: patientId, event }),
            });

            if (!response.ok) throw new Error('Failed to add event');
            return await response.json();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    const updateCalendarEvent = useCallback(async (patientId: string, eventId: string, event: any) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/api/calendar/event/${eventId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ patient_id: patientId, event }),
            });

            if (!response.ok) throw new Error('Failed to update event');
            return await response.json();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    const deleteCalendarEvent = useCallback(async (patientId: string, eventId: string) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/api/calendar/event/${eventId}?patient_id=${patientId}`, {
                method: 'DELETE',
            });

            if (!response.ok) throw new Error('Failed to delete event');
            return await response.json();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            return null;
        } finally {
            setLoading(false);
        }
    }, []);

    return {
        loading,
        error,
        signup,
        login,
        sendOtp,
        verifyOtp,
        analyzeImage,
        getPatient,
        getCalendar,
        generateCalendar,
        addCalendarEvent,
        updateCalendarEvent,
        deleteCalendarEvent,
    };
}

