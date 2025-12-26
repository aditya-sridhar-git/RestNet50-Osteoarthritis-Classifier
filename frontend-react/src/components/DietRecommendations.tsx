import type { DietRecommendation } from '../types';

interface DietRecommendationsProps {
    recommendations: DietRecommendation[];
    source: 'ai' | 'static';
}

export default function DietRecommendations({ recommendations, source }: DietRecommendationsProps) {
    if (!recommendations || recommendations.length === 0) {
        return (
            <div className="result-item">
                <div className="item-header">
                    <h3 className="item-title">
                        <span className="item-icon">🥗</span>
                        Diet Recommendations
                    </h3>
                </div>
                <div className="empty-state">
                    <p className="empty-state-text">No diet recommendations available</p>
                </div>
            </div>
        );
    }

    return (
        <div className="result-item">
            <div className="item-header">
                <h3 className="item-title">
                    <span className="item-icon">🥗</span>
                    Diet Recommendations
                </h3>
                {source === 'ai' && (
                    <span className="ai-badge">
                        ✨ AI Generated
                    </span>
                )}
            </div>
            <div className="recommendation-grid">
                {recommendations.map((rec, index) => (
                    <div key={index} className="recommendation-card">
                        <div className="recommendation-category">{rec.category}</div>
                        <ul className="recommendation-items">
                            {rec.items.map((item, i) => (
                                <li key={i}>{item}</li>
                            ))}
                        </ul>
                        <div className="recommendation-frequency">
                            📅 {rec.frequency}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
