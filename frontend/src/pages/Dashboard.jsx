import React, { useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import InsightPanel from '../components/InsightPanel';
import UrgencyBanner from '../components/UrgencyBanner';
import { downloadTextReport } from '../utils/report';
import {
  UploadCloud,
  AlertCircle,
  CheckCircle2,
  Activity,
  FileImage,
  Download,
} from 'lucide-react';

export default function Dashboard() {
  const { token } = useAuth();
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (selectedFile) => {
    setError(null);
    if (!selectedFile) return;

    if (!selectedFile.type.startsWith('image/')) {
      setError('Please select a valid image file (JPG, PNG)');
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('Image size should be less than 10MB');
      return;
    }

    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setResult(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files?.[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/predictions/predict', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Analysis failed');
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const clearSelection = () => {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const getConfidenceColor = (conf) => {
    if (conf >= 0.8) return 'text-success';
    if (conf >= 0.5) return 'text-warning';
    return 'text-error';
  };

  return (
    <div className="layout">
      <Navbar active="dashboard" />

      <main className="container">
        <div className="page-header mb-6">
          <h1>Skin Analysis</h1>
          <p className="text-muted">Upload an image for AI-powered screening and health insights</p>
        </div>

        <div className="dashboard-grid">
          <div className="card upload-card">
            <div className="card-header">
              <h2>New Scan</h2>
              <p>Drag & drop or browse for a skin image</p>
            </div>

            <div
              className={`dropzone ${isDragging ? 'dragging' : ''} ${previewUrl ? 'has-image' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => !previewUrl && fileInputRef.current?.click()}
            >
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept="image/jpeg,image/png,image/jpg"
                onChange={(e) => handleFileChange(e.target.files[0])}
              />

              {previewUrl ? (
                <div className="preview-container">
                  <img src={previewUrl} alt="Preview" className="image-preview" />
                  <div className="preview-overlay">
                    <button
                      onClick={(e) => { e.stopPropagation(); clearSelection(); }}
                      className="btn-secondary btn-sm"
                    >
                      Change Image
                    </button>
                  </div>
                </div>
              ) : (
                <div className="dropzone-content">
                  <div className="icon-circle">
                    <UploadCloud size={32} />
                  </div>
                  <h3>Drag & drop an image here</h3>
                  <p>or click to browse from your computer</p>
                  <span className="text-xs text-muted">Supports JPG, PNG (Max 10MB)</span>
                </div>
              )}
            </div>

            {error && (
              <div className="alert alert-error mt-4">
                <AlertCircle size={18} />
                <span>{error}</span>
              </div>
            )}

            <div className="actions mt-4">
              <button
                onClick={handleAnalyze}
                disabled={!file || isLoading}
                className="btn-primary w-full"
              >
                {isLoading ? (
                  <>
                    <div className="spinner" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Activity size={18} />
                    Run Analysis
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="card results-card">
            <div className="card-header">
              <h2>Results</h2>
              <p>Classification, risk level, and health insights</p>
            </div>

            {isLoading ? (
              <div className="results-loading">
                <div className="pulse-circle" />
                <p>Analyzing image patterns...</p>
              </div>
            ) : result ? (
              <div className="results-content fade-in">
                <UrgencyBanner risk={result.insights?.risk} />

                <div className="primary-result">
                  <div className="result-badge">
                    <CheckCircle2
                      size={24}
                      className={getConfidenceColor(result.confidence)}
                    />
                  </div>
                  <div>
                    <h3 className="result-class capitalize">
                      {result.insights?.display_name || result.prediction}
                    </h3>
                    <p className="result-confidence">
                      Confidence:{' '}
                      <span className={`font-bold ${getConfidenceColor(result.confidence)}`}>
                        {(result.confidence * 100).toFixed(1)}%
                      </span>
                    </p>
                  </div>
                </div>

                <div className="divider" />

                <h4>Probabilities</h4>
                <div className="prob-list">
                  {Object.entries(result.all_probabilities)
                    .sort(([, a], [, b]) => b - a)
                    .map(([className, prob]) => (
                      <div key={className} className="prob-item">
                        <div className="prob-header">
                          <span className="capitalize text-sm font-medium">{className}</span>
                          <span className="text-sm font-bold">{(prob * 100).toFixed(1)}%</span>
                        </div>
                        <div className="prob-bar-bg">
                          <div
                            className={`prob-bar-fill ${className === result.prediction ? 'bg-primary' : 'bg-secondary'}`}
                            style={{ width: `${Math.max(prob * 100, 1)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                </div>

                <InsightPanel insights={result.insights} />

                <button
                  onClick={() => downloadTextReport(result)}
                  className="btn-secondary w-full mt-4"
                >
                  <Download size={18} />
                  Download Report
                </button>
              </div>
            ) : (
              <div className="results-empty">
                <FileImage size={48} className="text-muted opacity-50 mb-4" />
                <p className="text-muted">Upload an image and run analysis to see results.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
