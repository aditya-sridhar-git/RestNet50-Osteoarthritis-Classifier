interface SettingsProps {
    language: 'en' | 'kn';
    onLanguageChange: (lang: 'en' | 'kn') => void;
}

export default function Settings({ language, onLanguageChange }: SettingsProps) {
    return (
        <div className="results-card">
            <h2 className="result-title" style={{ marginBottom: '1.5rem' }}>Settings</h2>

            <div className="result-item">
                <h3 className="item-title" style={{ marginBottom: '1.25rem' }}>
                    <span className="item-icon">🌐</span>
                    Language Preference
                </h3>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                    Choose your preferred language for recommendations and reminders.
                </p>

                <div className="language-toggle-group">
                    <button
                        className={`language-btn ${language === 'en' ? 'active' : ''}`}
                        onClick={() => onLanguageChange('en')}
                    >
                        <span className="lang-icon">🇺🇸</span>
                        English
                    </button>
                    <button
                        className={`language-btn ${language === 'kn' ? 'active' : ''}`}
                        onClick={() => onLanguageChange('kn')}
                    >
                        <span className="lang-icon">🇮🇳</span>
                        ಕನ್ನಡ (Kannada)
                    </button>
                </div>
            </div>

            <div className="result-item" style={{ marginTop: '1.5rem' }}>
                <h3 className="item-title" style={{ marginBottom: '1rem' }}>
                    <span className="item-icon">ℹ️</span>
                    Information
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    Switching the language will update all diet suggestions, exercise plans, and health reminders to your chosen language.
                </p>
            </div>
        </div>
    );
}
