import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import InsightPanel from '../components/InsightPanel';
import UrgencyBanner from '../components/UrgencyBanner';
import AuthenticatedImage from '../components/AuthenticatedImage';
import { downloadTextReport } from '../utils/report';
import { AlertCircle, ArrowLeft, Download } from 'lucide-react';

export default function HistoryDetail() {
  const { id } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [record, setRecord] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const res = await fetch(`/api/predictions/${id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error('Scan not found');
        setRecord(await res.json());
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDetail();
  }, [id, token]);

  const reportData = record
    ? {
        id: record.id,
        file: record.filename,
        prediction: record.predicted_class,
        confidence: record.confidence,
        all_probabilities: record.all_probabilities,
        risk_level: record.risk_level,
        insights: record.insights,
        timestamp: record.created_at,
      }
    : null;

  return (
    <div className="layout">
      <Navbar active="history" />

      <main className="container max-w-4xl">
        <button onClick={() => navigate('/history')} className="btn-nav mb-4">
          <ArrowLeft size={18} />
          Back to History
        </button>

        {error && (
          <div className="alert alert-error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="spinner large" />
          </div>
        ) : record ? (
          <div className="detail-grid">
            <div className="card">
              {record.image_url ? (
                <AuthenticatedImage
                  src={record.image_url}
                  token={token}
                  alt={record.filename}
                  className="detail-image"
                />
              ) : (
                <div className="auth-image-placeholder detail-image">No image stored</div>
              )}

              <div className="mt-4">
                <h2 className="capitalize">{record.insights?.display_name || record.predicted_class}</h2>
                <p className="text-muted text-sm">{record.filename}</p>
                <p className="mt-2">
                  Confidence:{' '}
                  <strong>{(record.confidence * 100).toFixed(1)}%</strong>
                </p>
                <p className="text-muted text-sm">
                  {new Date(record.created_at).toLocaleString()}
                </p>
              </div>

              <button
                onClick={() => downloadTextReport(reportData)}
                className="btn-secondary w-full mt-4"
              >
                <Download size={18} />
                Download Report
              </button>
            </div>

            <div className="card">
              <UrgencyBanner risk={record.insights?.risk} />
              <InsightPanel insights={record.insights} />
            </div>
          </div>
        ) : null}
      </main>
    </div>
  );
}
