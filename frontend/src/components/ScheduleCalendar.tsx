import { useState, useMemo } from 'react';
import type { CalendarEvent, Alert } from '../types';
import { ALERT_TYPES } from '../types';
import CalendarEventModal from './CalendarEventModal';

interface ScheduleCalendarProps {
    alerts: (Alert | CalendarEvent)[];
    selectedDate: Date;
    onDateSelect: (date: Date) => void;
    onAddEvent?: (event: Partial<CalendarEvent>) => Promise<void>;
    onUpdateEvent?: (eventId: string, event: Partial<CalendarEvent>) => Promise<void>;
    onDeleteEvent?: (eventId: string) => Promise<void>;
    onRegenerateCalendar?: () => Promise<void>;
    loading?: boolean;
    language: 'en' | 'kn';
}

export default function ScheduleCalendar({
    alerts,
    selectedDate,
    onDateSelect,
    onAddEvent,
    onUpdateEvent,
    onDeleteEvent,
    onRegenerateCalendar,
    loading = false,
    language,
}: ScheduleCalendarProps) {
    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [modalOpen, setModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
    const [editingEvent, setEditingEvent] = useState<CalendarEvent | null>(null);

    const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    const calendarDays = useMemo(() => {
        const year = currentMonth.getFullYear();
        const month = currentMonth.getMonth();

        const firstDay = new Date(year, month, 1);

        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());

        const days = [];
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        for (let i = 0; i < 42; i++) {
            const date = new Date(startDate);
            date.setDate(startDate.getDate() + i);

            // Get alerts for this day based on frequency
            const dayAlerts = alerts.filter(alert => {
                if (alert.frequency === 'daily') return true;
                if (alert.frequency === 'weekly') {
                    const dayNames = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
                    const dayName = dayNames[date.getDay()];
                    if (alert.frequency.includes(',')) {
                        return alert.frequency.toLowerCase().includes(dayName);
                    }
                    return true;
                }
                if (typeof alert.frequency === 'string' && alert.frequency.includes(',')) {
                    const dayNames = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
                    const dayName = dayNames[date.getDay()];
                    return alert.frequency.toLowerCase().includes(dayName);
                }
                if (alert.frequency === 'monthly') {
                    return date.getDate() === 1;
                }
                return false;
            });

            days.push({
                date,
                dayNumber: date.getDate(),
                isCurrentMonth: date.getMonth() === month,
                isToday: date.getTime() === today.getTime(),
                isSelected: date.toDateString() === selectedDate.toDateString(),
                alerts: dayAlerts,
            });
        }

        return days;
    }, [currentMonth, alerts, selectedDate]);

    const selectedDateAlerts = useMemo(() => {
        return alerts.filter(alert => {
            if (alert.frequency === 'daily') return true;
            if (alert.frequency === 'weekly') {
                const dayNames = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
                const dayName = dayNames[selectedDate.getDay()];
                if (alert.frequency.includes(',')) {
                    return alert.frequency.toLowerCase().includes(dayName);
                }
                return true;
            }
            if (typeof alert.frequency === 'string' && alert.frequency.includes(',')) {
                const dayNames = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
                const dayName = dayNames[selectedDate.getDay()];
                return alert.frequency.toLowerCase().includes(dayName);
            }
            if (alert.frequency === 'monthly') {
                return selectedDate.getDate() === 1;
            }
            return false;
        });
    }, [alerts, selectedDate]);

    const prevMonth = () => {
        setCurrentMonth(prev => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
    };

    const nextMonth = () => {
        setCurrentMonth(prev => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
    };

    const formatMonth = (date: Date) => {
        return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    };

    const getAlertIcon = (type: Alert['type']) => {
        return ALERT_TYPES.find(t => t.type === type)?.icon || '🔔';
    };

    const handleAddEvent = () => {
        setEditingEvent(null);
        setModalMode('add');
        setModalOpen(true);
    };

    const handleEditEvent = (alert: Alert | CalendarEvent) => {
        setEditingEvent(alert as CalendarEvent);
        setModalMode('edit');
        setModalOpen(true);
    };

    const handleSaveEvent = async (eventData: Partial<CalendarEvent>) => {
        if (modalMode === 'add' && onAddEvent) {
            await onAddEvent(eventData);
        } else if (modalMode === 'edit' && editingEvent && onUpdateEvent) {
            await onUpdateEvent((editingEvent as CalendarEvent).eventId, eventData);
        }
        setModalOpen(false);
    };

    const handleDeleteEvent = async (eventId: string) => {
        if (onDeleteEvent && confirm('Are you sure you want to delete this event?')) {
            await onDeleteEvent(eventId);
        }
    };

    if (alerts.length === 0) {
        return (
            <div className="calendar-section">
                <div className="empty-state" style={{ padding: '3rem' }}>
                    <div className="empty-state-icon">📅</div>
                    <p className="empty-state-text" style={{ marginBottom: '1rem' }}>
                        No schedule available yet
                    </p>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                        Upload an X-ray to get personalized AI-generated reminders based on your analysis
                    </p>
                    <div className="empty-state-actions">
                        {onRegenerateCalendar && (
                            <button
                                className="btn btn-primary"
                                onClick={onRegenerateCalendar}
                                disabled={loading}
                            >
                                {loading ? '⏳ Generating...' : '✨ Generate AI Calendar'}
                            </button>
                        )}
                        {onAddEvent && (
                            <button className="btn btn-secondary" onClick={handleAddEvent}>
                                ➕ Add Custom Event
                            </button>
                        )}
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="calendar-section">
            <div className="calendar-header">
                <h2 className="result-title">
                    {language === 'en' ? 'Your Health Schedule' : 'ನಿಮ್ಮ ಆರೋಗ್ಯ ವೇಳಾಪಟ್ಟಿ'}
                </h2>
                <div className="calendar-nav">
                    <button className="calendar-nav-btn" onClick={prevMonth} aria-label="Previous month">
                        ←
                    </button>
                    <span className="calendar-month">{formatMonth(currentMonth)}</span>
                    <button className="calendar-nav-btn" onClick={nextMonth} aria-label="Next month">
                        →
                    </button>
                </div>
            </div>

            <div className="schedule-info">
                <span className="ai-badge">
                    {language === 'en' ? '✨ AI Generated Schedule' : '✨ AI ರಚಿತ ವೇಳಾಪಟ್ಟಿ'}
                </span>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
                    {language === 'en'
                        ? 'These reminders are personalized based on your age, medical history, and diagnosis'
                        : 'ಈ ಜ್ಞಾಪನೆಗಳು ನಿಮ್ಮ ವಯಸ್ಸು, ವೈದ್ಯಕೀಯ ಇತಿಹಾಸ ಮತ್ತು ರೋಗನಿರ್ಣಯದ ಆಧಾರದ ಮೇಲೆ ವೈಯಕ್ತೀಕರಿಸಲ್ಪಟ್ಟಿವೆ'}
                </p>
            </div>

            <div className="calendar-actions">
                {onAddEvent && (
                    <button className="btn btn-secondary btn-sm" onClick={handleAddEvent}>
                        ➕ Add Event
                    </button>
                )}
                {onRegenerateCalendar && (
                    <button
                        className="btn btn-secondary btn-sm"
                        onClick={onRegenerateCalendar}
                        disabled={loading}
                    >
                        {loading ? '⏳...' : '🔄 Regenerate'}
                    </button>
                )}
            </div>

            <div className="calendar-grid">
                {daysOfWeek.map(day => (
                    <div key={day} className="calendar-day-header">{day}</div>
                ))}

                {calendarDays.map((day, index) => (
                    <div
                        key={index}
                        className={`calendar-day ${!day.isCurrentMonth ? 'other-month' : ''} ${day.isToday ? 'today' : ''} ${day.isSelected ? 'selected' : ''}`}
                        onClick={() => onDateSelect(day.date)}
                    >
                        <span className="calendar-day-number">{day.dayNumber}</span>
                        <div className="calendar-day-dots">
                            {day.alerts.slice(0, 3).map((alert, i) => (
                                <span key={i} className={`calendar-dot ${alert.type}`} />
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            <div className="alerts-section">
                <div className="alerts-header">
                    <h3 className="alerts-title">
                        {language === 'en' ? 'Schedule for ' : 'ವೇಳಾಪಟ್ಟಿ '}
                        {selectedDate.toLocaleDateString(language === 'en' ? 'en-US' : 'kn-IN', { weekday: 'long', month: 'short', day: 'numeric' })}
                    </h3>
                </div>

                {selectedDateAlerts.length === 0 ? (
                    <div className="empty-state">
                        <p className="empty-state-text">No scheduled activities for this day</p>
                    </div>
                ) : (
                    <div className="alerts-list">
                        {selectedDateAlerts.map((alert, index) => {
                            const calendarEvent = alert as CalendarEvent;
                            const hasEventId = 'eventId' in alert;

                            return (
                                <div key={hasEventId ? calendarEvent.eventId : index} className="alert-item">
                                    <div className={`alert-icon ${alert.type}`}>
                                        {getAlertIcon(alert.type)}
                                    </div>
                                    <div className="alert-content">
                                        <div className="alert-title-row">
                                            <span className="alert-title">
                                                {language === 'en' ? alert.title : (alert.title_kn || alert.title)}
                                            </span>
                                            <span className="alert-time">{alert.time}</span>
                                        </div>
                                        <p className="alert-description">
                                            {language === 'en' ? alert.description : (alert.description_kn || alert.description)}
                                        </p>
                                        <div className="alert-meta">
                                            <span className="alert-frequency">
                                                🔄 {language === 'en' ? alert.frequency : (alert.frequency_kn || alert.frequency)}
                                            </span>
                                            {hasEventId && (
                                                <span className={`alert-source ${calendarEvent.isAiGenerated ? 'ai' : 'custom'}`}>
                                                    {calendarEvent.isAiGenerated ? '🤖 AI' : '👤 Custom'}
                                                    {calendarEvent.isModified && ' (modified)'}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    {hasEventId && (onUpdateEvent || onDeleteEvent) && (
                                        <div className="alert-actions">
                                            {onUpdateEvent && (
                                                <button
                                                    className="alert-action-btn edit"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleEditEvent(alert);
                                                    }}
                                                    title="Edit event"
                                                >
                                                    ✏️
                                                </button>
                                            )}
                                            {onDeleteEvent && (
                                                <button
                                                    className="alert-action-btn delete"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDeleteEvent(calendarEvent.eventId);
                                                    }}
                                                    title="Delete event"
                                                >
                                                    🗑️
                                                </button>
                                            )}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            <div className="schedule-legend">
                <h4 style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>Legend</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
                    {ALERT_TYPES.slice(0, 5).map(type => (
                        <div key={type.type} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span className={`calendar-dot ${type.type}`} style={{ width: '10px', height: '10px' }} />
                            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{type.label}</span>
                        </div>
                    ))}
                </div>
            </div>

            <CalendarEventModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                onSave={handleSaveEvent}
                event={editingEvent}
                mode={modalMode}
            />
        </div>
    );
}
