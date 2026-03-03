import type { ExercisePlan as ExercisePlanType } from '../types';

interface ExercisePlanProps {
    exercises: ExercisePlanType[];
    source: 'ai' | 'static';
}

export default function ExercisePlan({ exercises, source }: ExercisePlanProps) {
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
                        <div className="exercise-name">{exercise.name}</div>
                        <div className="exercise-details">
                            <div className="exercise-detail">
                                <div className="exercise-detail-label">Duration</div>
                                <div className="exercise-detail-value">{exercise.duration}</div>
                            </div>
                            <div className="exercise-detail">
                                <div className="exercise-detail-label">Frequency</div>
                                <div className="exercise-detail-value">{exercise.frequency}</div>
                            </div>
                            <div className="exercise-detail">
                                <div className="exercise-detail-label">Intensity</div>
                                <div className="exercise-detail-value">{exercise.intensity}</div>
                            </div>
                        </div>
                        <div className="exercise-tips">
                            💡 {exercise.tips}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
