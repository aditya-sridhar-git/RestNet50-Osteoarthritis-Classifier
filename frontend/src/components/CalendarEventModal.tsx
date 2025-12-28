import { useState, useEffect } from 'react';
import type { CalendarEvent, Alert } from '../types';
import { ALERT_TYPES } from '../types';

interface CalendarEventModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (event: Partial<CalendarEvent>) => void;
    event?: CalendarEvent | null;
    mode: 'add' | 'edit';
}

export default function CalendarEventModal({
    isOpen,
    onClose,
    onSave,
    event,
    mode,
}: CalendarEventModalProps) {
    const [formData, setFormData] = useState({
        type: 'reminder' as Alert['type'],
        title: '',
        description: '',
        time: '09:00',
        frequency: 'daily',
    });

    useEffect(() => {
        if (event && mode === 'edit') {
            setFormData({
                type: event.type,
                title: event.title,
                description: event.description,
                time: event.time,
                frequency: event.frequency,
            });
        } else {
            setFormData({
                type: 'reminder',
                title: '',
                description: '',
                time: '09:00',
                frequency: 'daily',
            });
        }
    }, [event, mode, isOpen]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSave(formData);
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3 className="modal-title">
                        {mode === 'add' ? '✨ Add New Event' : '✏️ Edit Event'}
                    </h3>
                    <button className="modal-close" onClick={onClose}>×</button>
                </div>

                <form onSubmit={handleSubmit} className="modal-form">
                    <div className="form-group">
                        <label className="form-label">Event Type</label>
                        <select
                            className="form-select"
                            value={formData.type}
                            onChange={(e) => setFormData({ ...formData, type: e.target.value as Alert['type'] })}
                        >
                            {ALERT_TYPES.map((type) => (
                                <option key={type.type} value={type.type}>
                                    {type.icon} {type.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Title</label>
                        <input
                            type="text"
                            className="form-input"
                            value={formData.title}
                            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                            placeholder="e.g., Morning Walk"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Description</label>
                        <textarea
                            className="form-textarea"
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            placeholder="Add details about this event..."
                            rows={3}
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label className="form-label">Time</label>
                            <input
                                type="time"
                                className="form-input"
                                value={formData.time}
                                onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Frequency</label>
                            <select
                                className="form-select"
                                value={formData.frequency}
                                onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                            >
                                <option value="once">Once</option>
                                <option value="daily">Daily</option>
                                <option value="weekly">Weekly</option>
                                <option value="mon,wed,fri">Mon, Wed, Fri</option>
                                <option value="tue,thu">Tue, Thu</option>
                                <option value="monthly">Monthly</option>
                            </select>
                        </div>
                    </div>

                    <div className="modal-actions">
                        <button type="button" className="btn btn-secondary" onClick={onClose}>
                            Cancel
                        </button>
                        <button type="submit" className="btn btn-primary">
                            {mode === 'add' ? 'Add Event' : 'Save Changes'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
