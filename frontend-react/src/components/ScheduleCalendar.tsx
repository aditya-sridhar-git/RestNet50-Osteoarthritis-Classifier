import { useState, useMemo } from 'react';
import type { Alert } from '../types';
import { ALERT_TYPES } from '../types';

interface ScheduleCalendarProps {
    alerts: Alert[];
    selectedDate: Date;
    onDateSelect: (date: Date) => void;
}

export default function ScheduleCalendar({
    alerts,
    selectedDate,
    onDateSelect,
}: ScheduleCalendarProps) {
    const [currentMonth, setCurrentMonth] = useState(new Date());

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
                    // Show on same day of week
                    const dayNames = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
                    const dayName = dayNames[date.getDay()];
                    // Check if frequency contains specific days like "mon,wed,fri"
                    if (alert.frequency.includes(',')) {
                        return alert.frequency.toLowerCase().includes(dayName);
                    }
                    return true;
                }
                if (alert.frequency === 'monthly') {
                    // Show on same day of month
                    return date.getDate() === 1; // Default to 1st of month
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

    if (alerts.length === 0) {
        return (
            <div className="calendar-section">
                <div className="empty-state" style={{ padding: '3rem' }}>
                    <div className="empty-state-icon">📅</div>
                    <p className="empty-state-text" style={{ marginBottom: '1rem' }}>
                        No schedule available yet
                    </p>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                        Upload an X-ray to get personalized reminders based on your analysis
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="calendar-section">
            <div className="calendar-header">
                <h2 className="result-title">Your Health Schedule</h2>
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
                <span className="ai-badge">✨ AI Generated Schedule</span>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
                    These reminders are automatically generated based on your diagnosis
                </p>
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
                        Schedule for {selectedDate.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
                    </h3>
                </div>

                {selectedDateAlerts.length === 0 ? (
                    <div className="empty-state">
                        <p className="empty-state-text">No scheduled activities for this day</p>
                    </div>
                ) : (
                    <div className="alerts-list">
                        {selectedDateAlerts.map((alert, index) => (
                            <div key={index} className="alert-item">
                                <div className={`alert-icon ${alert.type}`}>
                                    {getAlertIcon(alert.type)}
                                </div>
                                <div className="alert-content">
                                    <div className="alert-title-row">
                                        <span className="alert-title">{alert.title}</span>
                                        <span className="alert-time">{alert.time}</span>
                                    </div>
                                    <p className="alert-description">{alert.description}</p>
                                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                        🔄 {alert.frequency}
                                    </span>
                                </div>
                            </div>
                        ))}
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
        </div>
    );
}
