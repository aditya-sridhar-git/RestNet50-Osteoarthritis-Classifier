import type { AnalysisResult } from '../types';
import SeverityMeter from './SeverityMeter';
import DietRecommendations from './DietRecommendations';
import ExercisePlan from './ExercisePlan';

interface AnalysisResultsProps {
    result: AnalysisResult;
    language: 'en' | 'kn';
    onAddSuggestedAlerts: () => void;
}

export default function AnalysisResults({ result, language, onAddSuggestedAlerts }: AnalysisResultsProps) {
    return (
        <div className="results-section">
            <div className="results-card">
                <div className="result-header">
                    <h2 className="result-title">Analysis Results</h2>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        {result.source === 'ai' && (
                            <span className="ai-badge">✨ AI Powered</span>
                        )}
                        <div className={`severity-badge ${result.severity.toLowerCase()}`}>
                            {result.severity}
                        </div>
                    </div>
                </div>

                <div className="result-grid">
                    <SeverityMeter severity={result.severity} />

                    <DietRecommendations
                        recommendations={result.diet}
                        source={result.source}
                        language={language}
                    />

                    <ExercisePlan
                        exercises={result.exercise}
                        source={result.source}
                        language={language}
                    />

                    {result.alerts && result.alerts.length > 0 && (
                        <div className="result-item">
                            <div className="item-header">
                                <h3 className="item-title">
                                    <span className="item-icon">🔔</span>
                                    Suggested Reminders
                                </h3>
                                <button
                                    className="btn btn-primary"
                                    style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}
                                    onClick={() => onAddSuggestedAlerts()}
                                >
                                    Add All to Calendar
                                </button>
                            </div>
                            <div className="recommendation-grid">
                                {result.alerts.slice(0, 4).map((alert, index) => (
                                    <div key={index} className="recommendation-card">
                                        <div className="recommendation-category">
                                            {language === 'en' ? (
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
                                            {language === 'en' ? (
                                                <p className="en-text">{alert.description}</p>
                                            ) : (
                                                <p className="kn-text">{alert.description_kn || alert.description}</p>
                                            )}
                                        </div>
                                        <div className="recommendation-frequency">
                                            {language === 'en' ? (
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
