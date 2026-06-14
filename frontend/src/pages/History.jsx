import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import AuthenticatedImage from '../components/AuthenticatedImage';
import { Clock, FileImage, AlertCircle } from 'lucide-react';

const RISK_BADGE = {
  high: 'risk-badge-high',
  medium: 'risk-badge-medium',
  low: 'risk-badge-low',
};

export default function History() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch('/api/predictions/history', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error('Failed to fetch history');
        const data = await res.json();
        setHistory(data.predictions || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchHistory();
  }, [token]);

  const formatDate = (isoString) =>
    new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(isoString));

  const getConfidenceColor = (conf) => {
    if (conf >= 0.8) return 'text-success';
    if (conf >= 0.5) return 'text-warning';
    return 'text-error';
  };

  return (
    <div className="layout">
      <Navbar active="history" />

      <main className="container max-w-4xl">
        <div className="page-header mb-6">
          <h1>Scan History</h1>
          <p className="text-muted">Your past analyses with saved images</p>
        </div>

        {error && (
          <div className="alert alert-error mb-6">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="spinner large" />
          </div>
        ) : history.length === 0 ? (
          <div className="card text-center py-12">
            <FileImage size={48} className="text-muted opacity-50 mx-auto mb-4" />
            <h3 className="text-lg font-medium">No scans yet</h3>
            <p className="text-muted mb-6">Run your first analysis from the dashboard.</p>
            <button onClick={() => navigate('/dashboard')} className="btn-primary inline-flex">
              New Analysis
            </button>
          </div>
        ) : (
          <div className="history-grid">
            {history.map((item) => (
              <div
                key={item.id}
                className="card history-card fade-in clickable"
                onClick={() => navigate(`/history/${item.id}`)}
              >
                {item.image_url ? (
                  <div className="history-card-img-wrapper">
                    <AuthenticatedImage
                      src={item.image_url}
                      token={token}
                      alt={item.filename}
                      className="history-thumb"
                    />
                  </div>
                ) : (
                  <div className="auth-image-placeholder history-thumb">No image stored</div>
                )}

                <div className="history-header">
                  <div className="history-file">
                    <FileImage size={18} className="text-muted" />
                    <span className="truncate" title={item.filename}>{item.filename}</span>
                  </div>
                  {item.risk_level && (
                    <span className={`risk-badge ${RISK_BADGE[item.risk_level] || ''}`}>
                      {item.risk_level}
                    </span>
                  )}
                </div>

                <div className="history-body mt-4">
                  <div className="mb-1 text-sm text-muted uppercase tracking-wider font-semibold">
                    Prediction
                  </div>
                  <div className="text-xl font-bold capitalize mb-2">{item.predicted_class}</div>

                  <div className="flex justify-between items-center text-sm">
                    <span className="text-muted flex items-center gap-1">
                      <Clock size={14} />
                      {formatDate(item.created_at)}
                    </span>
                    <span className={`font-bold ${getConfidenceColor(item.confidence)}`}>
                      {(item.confidence * 100).toFixed(1)}%
                    </span>
                  </div>

                  <div className="prob-bar-bg mt-2 h-1.5">
                    <div
                      className="prob-bar-fill bg-cyan h-full"
                      style={{ width: `${item.confidence * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
