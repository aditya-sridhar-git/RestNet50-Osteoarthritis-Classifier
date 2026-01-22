import type { ExercisePlan as ExercisePlanType } from '../types';

interface ExercisePlanProps {
    exercises: ExercisePlanType[];
    source: 'ai' | 'static';
    language: 'en' | 'kn';
}

export default function ExercisePlan({ exercises, source, language }: ExercisePlanProps) {
    if (!exercises || exercises.length === 0) {
        return (
            <div className="result-item">
                <div className="item-header">
                    <h3 className="item-title">
                        <span className="item-icon">🏃</span>
                        Exercise Plan
                    </h3>
                </div>
                <div className="empty-state">
                    <p className="empty-state-text">No exercise plan available</p>
                </div>
            </div>
        );
    }

    return (
        <div className="result-item">
            <div className="item-header">
                <h3 className="item-title">
                    <span className="item-icon">🏃</span>
                    Exercise Plan
                </h3>
                {source === 'ai' && (
                    <span className="ai-badge">
                        ✨ AI Generated
                    </span>
                )}
            </div>
            <div className="recommendation-grid">
                {exercises.map((exercise, index) => (
                    <div key={index} className="exercise-card">
                        <div className="exercise-name">
                            {language === 'en' ? exercise.name : (exercise.name_kn || exercise.name)}
                        </div>
                        <div className="exercise-details">
                            <div className="exercise-detail">
                                <div className="exercise-detail-label">Duration</div>
                                <div className="exercise-detail-value">
                                    {language === 'en' ? exercise.duration : (exercise.duration_kn || exercise.duration)}
                                </div>
                            </div>
                            <div className="exercise-detail">
                                <div className="exercise-detail-label">Frequency</div>
                                <div className="exercise-detail-value">
                                    {language === 'en' ? exercise.frequency : (exercise.frequency_kn || exercise.frequency)}
                                </div>
                            </div>
                            <div className="exercise-detail">
                                <div className="exercise-detail-label">Intensity</div>
                                <div className="exercise-detail-value">
                                    {language === 'en' ? exercise.intensity : (exercise.intensity_kn || exercise.intensity)}
                                </div>
                            </div>
                        </div>
                        <div className="exercise-tips">
                            💡 {language === 'en' ? exercise.tips : (exercise.tips_kn || exercise.tips)}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
