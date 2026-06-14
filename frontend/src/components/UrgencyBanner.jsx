import React from 'react';
import { AlertTriangle, Info, ShieldAlert } from 'lucide-react';

const CONFIG = {
  high: {
    icon: ShieldAlert,
    className: 'urgency-high',
    title: 'High priority',
  },
  medium: {
    icon: AlertTriangle,
    className: 'urgency-medium',
    title: 'Moderate attention',
  },
  low: {
    icon: Info,
    className: 'urgency-low',
    title: 'Low urgency',
  },
};

export default function UrgencyBanner({ risk }) {
  if (!risk) return null;

  const cfg = CONFIG[risk.level] || CONFIG.medium;
  const Icon = cfg.icon;

  return (
    <div className={`urgency-banner ${cfg.className}`}>
      <Icon size={22} />
      <div>
        <strong>{cfg.title}: {risk.label}</strong>
        <p>{risk.reason}</p>
      </div>
    </div>
  );
}
