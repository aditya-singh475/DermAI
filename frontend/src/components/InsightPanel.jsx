import React from 'react';
import { BookOpen, HeartPulse, Stethoscope, AlertCircle } from 'lucide-react';

export default function InsightPanel({ insights }) {
  if (!insights) return null;

  return (
    <div className="insight-panel fade-in">
      <div className="insight-header">
        <BookOpen size={20} className="text-cyan" />
        <h4>Health Insights</h4>
      </div>

      <p className="insight-description">{insights.description}</p>

      {insights.symptoms?.length > 0 && (
        <div className="insight-section">
          <h5><HeartPulse size={16} /> Common signs</h5>
          <ul>
            {insights.symptoms.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {insights.care_tips?.length > 0 && (
        <div className="insight-section">
          <h5>General care tips</h5>
          <ul>
            {insights.care_tips.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="insight-section insight-doctor">
        <h5><Stethoscope size={16} /> When to see a doctor</h5>
        <p>{insights.when_to_see_doctor}</p>
      </div>

      {insights.alternatives?.length > 0 && (
        <div className="insight-section">
          <h5>Other possibilities</h5>
          <div className="alt-chips">
            {insights.alternatives.map((alt) => (
              <span key={alt.class} className="alt-chip">
                {alt.class} ({(alt.probability * 100).toFixed(0)}%)
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="insight-disclaimer">
        <AlertCircle size={14} />
        <span>{insights.disclaimer}</span>
      </div>
    </div>
  );
}
