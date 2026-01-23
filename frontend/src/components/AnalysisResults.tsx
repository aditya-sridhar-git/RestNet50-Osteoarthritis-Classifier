import { useState, useCallback } from 'react';
import type { AnalysisResult } from '../types';
import { SEVERITY_LEVELS } from '../types';
import SeverityMeter from './SeverityMeter';
import DietRecommendations from './DietRecommendations';
import ExercisePlan from './ExercisePlan';

interface AnalysisResultsProps {
    result: AnalysisResult;
    language: 'en' | 'kn';
    onAddSuggestedAlerts: () => void;
}

export default function AnalysisResults({ result, language: initialLanguage, onAddSuggestedAlerts }: AnalysisResultsProps) {
    const [displayLanguage, setDisplayLanguage] = useState<'en' | 'kn'>(initialLanguage);

    const speak = useCallback((text: string, lang: 'en' | 'kn') => {
        const synth = window.speechSynthesis;
        if (!synth) return;

        synth.cancel();
        const utterance = new SpeechSynthesisUtterance(text);

        const voices = synth.getVoices();
        let selectedVoice: SpeechSynthesisVoice | undefined;

        if (lang === 'kn') {
            selectedVoice = voices.find(v => v.lang === 'kn-IN' || v.lang.startsWith('kn'));
            if (!selectedVoice) {
                selectedVoice = voices.find(v => v.lang === 'hi-IN' || v.lang.startsWith('hi'));
            }
        } else {
            selectedVoice = voices.find(v => v.lang.startsWith('en'));
        }

        if (selectedVoice) utterance.voice = selectedVoice;
        utterance.lang = lang === 'kn' ? 'kn-IN' : 'en-US';
        utterance.rate = 0.9;

        synth.speak(utterance);
    }, []);

    const speakInsights = () => {
        let text = "";
        if (displayLanguage === 'en') {
            text = `Your osteoarthritis severity is ${result.severity}. `;
            text += "Diet recommendations include: " + result.diet.map(d => d.category).join(", ") + ". ";
            text += "Exercises include: " + result.exercise.map(e => e.name).join(", ") + ".";
        } else {
            text = `ನಿಮ್ಮ ಅಸ್ಥಿಸಂಧಿವಾತದ ತೀವ್ರತೆಯು ${result.severity} ಆಗಿದೆ. `;
            text += "ಆಹಾರದ ಶಿಫಾರಸುಗಳು: " + result.diet.map(d => d.category_kn || d.category).join(", ") + ". ";
            text += "ವ್ಯಾಯಾಮಗಳು: " + result.exercise.map(e => e.name_kn || e.name).join(", ") + ".";
        }
        speak(text, displayLanguage);
    };

    return (
        <div className="results-section">
            <div className="results-card">
                <div className="result-header">
                    <h2 className="result-title">{displayLanguage === 'en' ? 'Analysis Results' : 'ವಿಶ್ಲೇಷಣಾ ಫಲಿತಾಂಶಗಳು'}</h2>
                    <div className="results-controls">
                        <div className="tts-toggle compact">
                            <div className="toggle-buttons">
                                <button
                                    className={`toggle-btn ${displayLanguage === 'en' ? 'active' : ''}`}
                                    onClick={() => setDisplayLanguage('en')}
                                >
                                    EN
                                </button>
                                <button
                                    className={`toggle-btn ${displayLanguage === 'kn' ? 'active' : ''}`}
                                    onClick={() => setDisplayLanguage('kn')}
                                >
                                    KN
                                </button>
                            </div>
                        </div>
                        <button className="speak-btn-insights" onClick={speakInsights} title="Read insights">
                            🔊
                        </button>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        {result.source === 'ai' && (
                            <span className="ai-badge">✨ {displayLanguage === 'en' ? 'AI Powered' : 'AI ಆಧಾರಿತ'}</span>
                        )}
                        <div className={`severity-badge ${result.severity.toLowerCase()}`}>
                            {displayLanguage === 'en' ? result.severity : (SEVERITY_LEVELS.find(s => s.level === result.severity)?.level_kn || result.severity)}
                        </div>
                    </div>
                </div>

                <div className="result-grid">
                    <SeverityMeter severity={result.severity} language={displayLanguage} />

                    <DietRecommendations
                        recommendations={result.diet}
                        source={result.source}
                        language={displayLanguage}
                    />

                    <ExercisePlan
                        exercises={result.exercise}
                        source={result.source}
                        language={displayLanguage}
                    />

                    {result.alerts && result.alerts.length > 0 && (
                        <div className="result-item">
                            <div className="item-header">
                                <h3 className="item-title">
                                    <span className="item-icon">🔔</span>
                                    {displayLanguage === 'en' ? 'Suggested Reminders' : 'ಸೂಚಿಸಲಾದ ಜ್ಞಾಪನೆಗಳು'}
                                </h3>
                                <button
                                    className="btn btn-primary"
                                    style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}
                                    onClick={() => onAddSuggestedAlerts()}
                                >
                                    {displayLanguage === 'en' ? 'Add All to Calendar' : 'ಕ್ಯಾಲೆಂಡರ್‌ಗೆ ಎಲ್ಲವನ್ನೂ ಸೇರಿಸಿ'}
                                </button>
                            </div>
                            <div className="recommendation-grid">
                                {result.alerts.slice(0, 4).map((alert, index) => (
                                    <div key={index} className="recommendation-card">
                                        <div className="recommendation-category">
                                            {displayLanguage === 'en' ? (
                                                <div className="en-text">
                                                    {alert.type === 'exercise' && '🏃 '}
                                                    {alert.type === 'medication' && '💊 '}
                                                    {alert.type === 'meal' && '🥗 '}
                                                    {alert.type === 'checkup' && '🏥 '}
                                                    {alert.type === 'hydration' && '💧 '}
                                                    {alert.title}
                                                </div>
                                            ) : (
                                                <div className="kn-text">
                                                    {alert.type === 'exercise' && '🏃 '}
                                                    {alert.type === 'medication' && '💊 '}
                                                    {alert.type === 'meal' && '🥗 '}
                                                    {alert.type === 'checkup' && '🏥 '}
                                                    {alert.type === 'hydration' && '💧 '}
                                                    {alert.title_kn || alert.title}
                                                </div>
                                            )}
                                        </div>
                                        <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                                            {displayLanguage === 'en' ? (
                                                <p className="en-text">{alert.description}</p>
                                            ) : (
                                                <p className="kn-text">{alert.description_kn || alert.description}</p>
                                            )}
                                        </div>
                                        <div className="recommendation-frequency">
                                            {displayLanguage === 'en' ? (
                                                <div className="en-text">🕐 {alert.time} • {alert.frequency}</div>
                                            ) : (
                                                <div className="kn-text">🕐 {alert.time} • {alert.frequency_kn || alert.frequency}</div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                <div className="disclaimer">
                    ⚠️ {result.disclaimer}
                </div>
            </div>
        </div>
    );
}
