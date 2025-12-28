import { useState } from 'react';

interface LoginFormProps {
    onLogin: (username: string, password: string) => Promise<void>;
    onSendOtp: (whatsappNumber: string) => Promise<string | null>;
    onVerifyOtp: (whatsappNumber: string, otp: string) => Promise<void>;
    onSwitchToSignup: () => void;
    loading: boolean;
    error: string | null;
}

export default function LoginForm({
    onLogin,
    onSendOtp,
    onVerifyOtp,
    onSwitchToSignup,
    loading,
    error
}: LoginFormProps) {
    const [loginMode, setLoginMode] = useState<'password' | 'otp'>('password');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [whatsappNumber, setWhatsappNumber] = useState('');
    const [otp, setOtp] = useState('');
    const [otpSent, setOtpSent] = useState(false);
    const [devOtp, setDevOtp] = useState<string | null>(null);

    const handlePasswordLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        await onLogin(username, password);
    };

    const handleSendOtp = async (e: React.FormEvent) => {
        e.preventDefault();
        const receivedOtp = await onSendOtp(whatsappNumber);
        // Always show OTP input after sending
        setOtpSent(true);
        // Set devOtp if returned (SMS failed), otherwise null
        setDevOtp(receivedOtp || null);
    };

    const handleVerifyOtp = async (e: React.FormEvent) => {
        e.preventDefault();
        await onVerifyOtp(whatsappNumber, otp);
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <div className="logo">
                        <div className="logo-icon">🦴</div>
                        <span className="logo-text">OsteoAI</span>
                    </div>
                    <h2 className="auth-title">Welcome Back</h2>
                    <p className="auth-subtitle">Login to access your health dashboard</p>
                </div>

                {/* Login mode toggle */}
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
                    <button
                        type="button"
                        className={`btn ${loginMode === 'password' ? 'btn-primary' : 'btn-secondary'}`}
                        style={{ flex: 1, padding: '0.75rem' }}
                        onClick={() => { setLoginMode('password'); setOtpSent(false); }}
                    >
                        Password
                    </button>
                    <button
                        type="button"
                        className={`btn ${loginMode === 'otp' ? 'btn-primary' : 'btn-secondary'}`}
                        style={{ flex: 1, padding: '0.75rem' }}
                        onClick={() => setLoginMode('otp')}
                    >
                        OTP
                    </button>
                </div>

                {loginMode === 'password' ? (
                    <form onSubmit={handlePasswordLogin} className="auth-form">
                        <div className="form-group">
                            <label className="input-label">Username</label>
                            <input
                                type="text"
                                className="input-field"
                                placeholder="Enter your username"
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
                                placeholder="Enter your password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
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
                            <span className="btn-text">{loading ? 'Logging in...' : 'Login'}</span>
                            <div className="btn-loader" />
                        </button>
                    </form>
                ) : !otpSent ? (
                    <form onSubmit={handleSendOtp} className="auth-form">
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
                            <span className="btn-text">{loading ? 'Sending...' : 'Send OTP'}</span>
                            <div className="btn-loader" />
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleVerifyOtp} className="auth-form">
                        <div className="form-group">
                            <label className="input-label">WhatsApp Number</label>
                            <input
                                type="tel"
                                className="input-field"
                                value={whatsappNumber}
                                disabled
                            />
                        </div>

                        <div className="form-group">
                            <label className="input-label">Enter OTP</label>
                            <input
                                type="text"
                                className="input-field otp-input"
                                placeholder="Enter 6-digit OTP"
                                maxLength={6}
                                value={otp}
                                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                                required
                            />
                        </div>

                        {devOtp && (
                            <div className="dev-otp-hint">
                                🔧 Development OTP: <strong>{devOtp}</strong>
                            </div>
                        )}

                        {error && (
                            <div className="auth-error">
                                ⚠️ {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            className={`btn btn-primary btn-full ${loading ? 'loading' : ''}`}
                            disabled={loading || otp.length !== 6}
                        >
                            <span className="btn-text">{loading ? 'Verifying...' : 'Verify & Login'}</span>
                            <div className="btn-loader" />
                        </button>

                        <button
                            type="button"
                            className="btn btn-secondary btn-full"
                            onClick={() => {
                                setOtpSent(false);
                                setOtp('');
                                setDevOtp(null);
                            }}
                            style={{ marginTop: '0.5rem' }}
                        >
                            Change Number
                        </button>
                    </form>
                )}

                <div className="auth-footer">
                    <p>Don't have an account?</p>
                    <button className="auth-link" onClick={onSwitchToSignup}>
                        Sign up here
                    </button>
                </div>
            </div>
        </div>
    );
}
