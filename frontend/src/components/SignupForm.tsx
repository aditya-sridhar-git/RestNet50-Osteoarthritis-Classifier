import { useState } from 'react';
import type { SignupData } from '../types';

interface SignupFormProps {
    onSignup: (data: SignupData) => Promise<void>;
    onSwitchToLogin: () => void;
    loading: boolean;
    error: string | null;
}

export default function SignupForm({ onSignup, onSwitchToLogin, loading, error }: SignupFormProps) {
    const [whatsappNumber, setWhatsappNumber] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [age, setAge] = useState('');
    const [pastHistory, setPastHistory] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        await onSignup({
            whatsappNumber,
            username,
            password,
            age: parseInt(age),
            pastHistory,
        });
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <div className="logo">
                        <div className="logo-icon">🦴</div>
                        <span className="logo-text">OsteoAI</span>
                    </div>
                    <h2 className="auth-title">Create Account</h2>
                    <p className="auth-subtitle">Sign up to track your knee health</p>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label className="input-label">WhatsApp Number</label>
                        <input
                            type="tel"
                            className="input-field"
                            placeholder="919876543210"
                            value={whatsappNumber}
                            onChange={(e) => setWhatsappNumber(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="input-label">Username</label>
                        <input
                            type="text"
                            className="input-field"
                            placeholder="Choose a username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="input-label">Password</label>
                        <input
                            type="password"
                            className="input-field"
                            placeholder="Create a password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label className="input-label">Age</label>
                            <input
                                type="number"
                                className="input-field"
                                placeholder="45"
                                min="1"
                                max="120"
                                value={age}
                                onChange={(e) => setAge(e.target.value)}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label className="input-label">Past History</label>
                            <input
                                type="text"
                                className="input-field"
                                placeholder="e.g., Asthma, Diabetes"
                                value={pastHistory}
                                onChange={(e) => setPastHistory(e.target.value)}
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="auth-error">
                            ⚠️ {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className={`btn btn-primary btn-full ${loading ? 'loading' : ''}`}
                        disabled={loading}
                    >
                        <span className="btn-text">{loading ? 'Creating Account...' : 'Create Account'}</span>
                        <div className="btn-loader" />
                    </button>
                </form>

                <div className="auth-footer">
                    <p>Already have an account?</p>
                    <button className="auth-link" onClick={onSwitchToLogin}>
                        Login here
                    </button>
                </div>
            </div>
        </div>
    );
}
