interface HeaderProps {
    activeTab: string;
    onTabChange: (tab: string) => void;
}

export default function Header({ activeTab, onTabChange }: HeaderProps) {
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
                    Analyze
                </button>
                <button
                    className={`nav-link ${activeTab === 'calendar' ? 'active' : ''}`}
                    onClick={() => onTabChange('calendar')}
                >
                    Calendar
                </button>
                <button
                    className={`nav-link ${activeTab === 'about' ? 'active' : ''}`}
                    onClick={() => onTabChange('about')}
                >
                    About
                </button>
            </nav>
        </header>
    );
}
