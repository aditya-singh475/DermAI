import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Activity, Mail, Lock, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function Login() {
  const [isRegistering, setIsRegistering] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    if (!username || !password) {
      setError('Username and password are required');
      setIsLoading(false);
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      setIsLoading(false);
      return;
    }

    const form = new URLSearchParams();
    form.append('username', username);
    form.append('password', password);

    try {
      if (isRegistering) {
        // Register flow
        const res = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        });
        
        const data = await res.json();
        
        if (!res.ok) {
          let errorMsg = 'Registration failed';
          if (data.detail) {
            if (typeof data.detail === 'string') {
              errorMsg = data.detail;
            } else if (Array.isArray(data.detail) && data.detail.length > 0) {
              errorMsg = data.detail[0].msg || 'Validation error';
            } else {
              errorMsg = JSON.stringify(data.detail);
            }
          }
          throw new Error(errorMsg);
        }
        
        setSuccess('Account created successfully! Please log in.');
        setIsRegistering(false);
        setPassword('');
      } else {
        // Login flow
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: form,
        });
        
        const data = await res.json();
        
        if (!res.ok) {
          throw new Error(data.detail || 'Invalid credentials');
        }
        
        login(data.access_token);
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-left">
        <div className="auth-brand">
          <div className="brand-logo">
            <Activity size={32} color="#06b6d4" />
          </div>
          <h1>DermAI</h1>
          <p>Free AI skin health screening</p>
        </div>
        <div className="auth-features">
          <div className="feature-item">
            <CheckCircle2 size={20} className="text-cyan" />
            <span>Instant AI classification</span>
          </div>
          <div className="feature-item">
            <CheckCircle2 size={20} className="text-cyan" />
            <span>Educational health insights — 100% free</span>
          </div>
          <div className="feature-item">
            <CheckCircle2 size={20} className="text-cyan" />
            <span>Secure scan history with saved images</span>
          </div>
        </div>
      </div>
      
      <div className="auth-right">
        <div className="auth-card">
          <h2>{isRegistering ? 'Create Account' : 'Welcome Back'}</h2>
          <p className="auth-subtitle">
            {isRegistering 
              ? 'Join to start analyzing skin conditions' 
              : 'Sign in to your account to continue'}
          </p>

          {error && (
            <div className="alert alert-error">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="alert alert-success">
              <CheckCircle2 size={18} />
              <span>{success}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label>Username</label>
              <div className="input-with-icon">
                <Mail size={18} className="input-icon" />
                <input
                  type="text"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Password</label>
              <div className="input-with-icon">
                <Lock size={18} className="input-icon" />
                <input
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                />
              </div>
            </div>

            <button type="submit" className="btn-primary auth-btn" disabled={isLoading}>
              {isLoading ? (
                <div className="spinner"></div>
              ) : (
                <>
                  {isRegistering ? 'Sign Up' : 'Sign In'}
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          <div className="auth-switch">
            <p>
              {isRegistering ? 'Already have an account?' : "Don't have an account?"}{' '}
              <button 
                type="button"
                className="btn-link"
                onClick={() => {
                  setIsRegistering(!isRegistering);
                  setError('');
                  setSuccess('');
                }}
                disabled={isLoading}
              >
                {isRegistering ? 'Sign In' : 'Create one'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
