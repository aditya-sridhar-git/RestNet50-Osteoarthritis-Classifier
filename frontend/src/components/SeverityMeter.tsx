import type { SeverityLevel } from '../types';
import { SEVERITY_LEVELS } from '../types';

interface SeverityMeterProps {
    severity: SeverityLevel;
}

export default function SeverityMeter({ severity }: SeverityMeterProps) {
    const config = SEVERITY_LEVELS.find(s => s.level === severity) || SEVERITY_LEVELS[0];

    return (
        <div className="result-item severity-meter-container">
            <h3 className="item-title">Severity Level</h3>
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
                        <span key={s.level}>{s.level}</span>
                    ))}
                </div>
            </div>
        </div>
    );
}
