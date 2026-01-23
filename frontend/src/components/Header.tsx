interface HeaderProps {
    activeTab: string;
    onTabChange: (tab: string) => void;
    language: 'en' | 'kn';
}

export default function Header({ activeTab, onTabChange, language }: HeaderProps) {
    return (
        <header className="header">
            <div className="logo">
                <div className="logo-icon">🦴</div>
                <span className="logo-text">OsteoAI</span>
            </div>
            <nav className="nav">
                <button
                    className={`nav-link ${activeTab === 'analyze' ? 'active' : ''}`}
                    onClick={() => onTabChange('analyze')}
                >
                    {language === 'en' ? 'Analyze' : 'ವಿಶ್ಲೇಷಿಸಿ'}
                </button>
                <button
                    className={`nav-link ${activeTab === 'calendar' ? 'active' : ''}`}
                    onClick={() => onTabChange('calendar')}
                >
                    {language === 'en' ? 'Calendar' : 'ಕ್ಯಾಲೆಂಡರ್'}
                </button>
                <button
                    className={`nav-link ${activeTab === 'chatbot' ? 'active' : ''}`}
                    onClick={() => onTabChange('chatbot')}
                >
                    {language === 'en' ? 'Chatbot' : 'ಚಾಟ್‌ಬಾಟ್'}
                </button>
                <button
                    className={`nav-link ${activeTab === 'about' ? 'active' : ''}`}
                    onClick={() => onTabChange('about')}
                >
                    {language === 'en' ? 'About' : 'ಮಾಹಿತಿ'}
                </button>
                <button
                    className={`nav-link ${activeTab === 'settings' ? 'active' : ''}`}
                    onClick={() => onTabChange('settings')}
                >
                    {language === 'en' ? 'Settings' : 'ಸೆಟ್ಟಿಂಗ್‌ಗಳು'}
                </button>
            </nav>
        </header>
    );
}
