import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Activity,
  ArrowRight,
  Brain,
  History,
  Shield,
  Stethoscope,
  Upload,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Landing() {
  const navigate = useNavigate();
  const { token } = useAuth();

  const goToApp = () => navigate(token ? '/dashboard' : '/login');

  return (
    <div className="landing">
      <header className="landing-nav">
        <div className="landing-brand">
          <Activity size={28} className="text-cyan" />
          <span>DermAI</span>
        </div>
        <button onClick={goToApp} className="btn-secondary btn-sm">
          {token ? 'Open App' : 'Sign In'}
          <ArrowRight size={16} />
        </button>
      </header>

      <section className="landing-hero">
        <div className="hero-badge">Free · AI-Powered · Instant Results</div>
        <h1>
          Understand your skin health with{' '}
          <span className="gradient-text">DermAI</span>
        </h1>
        <p className="hero-subtitle">
          Upload a skin image, get instant AI classification across 5 conditions,
          and receive clear educational guidance — completely free.
        </p>
        <div className="hero-actions">
          <button onClick={goToApp} className="btn-primary">
            Get Started Free
            <ArrowRight size={18} />
          </button>
          <a href="#how-it-works" className="btn-secondary">
            How it works
          </a>
        </div>
        <p className="hero-disclaimer">
          DermAI is for educational awareness only. It does not replace professional medical diagnosis.
        </p>
      </section>

      <section id="how-it-works" className="landing-section">
        <h2>How DermAI works</h2>
        <div className="steps-grid">
          <div className="step-card">
            <Upload size={28} className="text-cyan" />
            <h3>1. Upload</h3>
            <p>Take or upload a clear photo of the affected skin area.</p>
          </div>
          <div className="step-card">
            <Brain size={28} className="text-cyan" />
            <h3>2. Analyze</h3>
            <p>Our MobileNetV2 model classifies the image in seconds.</p>
          </div>
          <div className="step-card">
            <Stethoscope size={28} className="text-cyan" />
            <h3>3. Learn</h3>
            <p>Get condition-specific care tips and guidance on when to see a doctor.</p>
          </div>
          <div className="step-card">
            <History size={28} className="text-cyan" />
            <h3>4. Track</h3>
            <p>Review your scan history with saved images and risk levels.</p>
          </div>
        </div>
      </section>

      <section className="landing-section">
        <h2>What we detect</h2>
        <div className="conditions-grid">
          {['Acne', 'Benign Growths', 'Eczema', 'Fungal Infections', 'Melanoma'].map(
            (name) => (
              <div key={name} className="condition-chip">{name}</div>
            )
          )}
        </div>
      </section>

      <section className="landing-section features-section">
        <h2>Built for privacy</h2>
        <div className="features-grid">
          <div className="feature-card">
            <Shield size={24} className="text-cyan" />
            <h3>Completely Free</h3>
            <p>AI-powered analysis. No hidden fees, no subscription required.</p>
          </div>
          <div className="feature-card">
            <History size={24} className="text-cyan" />
            <h3>Your data stays yours</h3>
            <p>Images and history stored securely on your own server.</p>
          </div>
          <div className="feature-card">
            <Brain size={24} className="text-cyan" />
            <h3>Curated health insights</h3>
            <p>Educational content from a verified knowledge base, not guesswork.</p>
          </div>
        </div>
      </section>

      <footer className="landing-footer">
        <p>DermAI · AI Skin Health Screening</p>
        <p className="text-muted text-sm">
          Not a medical device. Always consult a dermatologist for diagnosis.
        </p>
      </footer>
    </div>
  );
}
