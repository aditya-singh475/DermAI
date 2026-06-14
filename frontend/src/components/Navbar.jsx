import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, LogOut, History, LayoutDashboard } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ active }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  return (
    <nav className="navbar">
      <div className="nav-brand clickable" onClick={() => navigate('/dashboard')}>
        <Activity size={24} className="text-cyan" />
        <span className="font-bold">DermAI</span>
      </div>
      <div className="nav-links">
        <button
          onClick={() => navigate('/dashboard')}
          className={`btn-nav ${active === 'dashboard' ? 'active' : ''}`}
        >
          <LayoutDashboard size={18} />
          Analyze
        </button>
        <button
          onClick={() => navigate('/history')}
          className={`btn-nav ${active === 'history' ? 'active' : ''}`}
        >
          <History size={18} />
          History
        </button>
        <button onClick={logout} className="btn-nav btn-nav-danger">
          <LogOut size={18} />
          Sign Out
        </button>
      </div>
    </nav>
  );
}
