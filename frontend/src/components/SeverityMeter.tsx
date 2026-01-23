import type { SeverityLevel } from '../types';
import { SEVERITY_LEVELS } from '../types';

interface SeverityMeterProps {
    severity: SeverityLevel;
    language: 'en' | 'kn';
}

export default function SeverityMeter({ severity, language }: SeverityMeterProps) {
    const config = SEVERITY_LEVELS.find(s => s.level === severity) || SEVERITY_LEVELS[0];

    return (
        <div className="result-item severity-meter-container">
            <h3 className="item-title">{language === 'en' ? 'Severity Level' : 'ತೀವ್ರತೆಯ ಮಟ್ಟ'}</h3>
            <div className="severity-meter">
                <div className="severity-track">
                    <div
                        className="severity-fill"
                        style={{
                            width: `${config.percent}%`,
                            background: config.color
                        }}
                    />
                </div>
                <div className="severity-labels">
                    {SEVERITY_LEVELS.map(s => (
                        <span key={s.level} style={{ color: s.level === severity ? s.color : 'var(--text-muted)' }}>
                            {language === 'en' ? s.level : s.level_kn}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
}
