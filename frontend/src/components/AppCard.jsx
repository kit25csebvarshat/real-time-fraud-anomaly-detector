import React from 'react';
import { ShieldCheck, ShieldAlert, CheckCircle2, AlertTriangle, ArrowUpRight, Sliders, Users, Calendar } from 'lucide-react';

export default function AppCard({ app, onSelect, onOpenSimulator, onTrust, onRevoke }) {
  const getBadgeStyle = (level) => {
    switch (level) {
      case 'CRITICAL':
        return 'badge-critical';
      case 'HIGH':
        return 'badge-high';
      case 'MEDIUM':
        return 'badge-medium';
      default:
        return 'badge-low';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'TRUSTED':
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">TRUSTED</span>;
      case 'REVIEW':
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">REVIEW REQUIRED</span>;
      case 'REVOKED':
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">REVOKED</span>;
      default:
        return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">ACTIVE</span>;
    }
  };

  return (
    <div className="glass-card p-5 rounded-2xl flex flex-col justify-between border border-slate-800/80 hover:border-indigo-500/30">
      <div className="space-y-3.5">
        
        {/* Card Header */}
        <div className="flex items-start justify-between">
          <div>
            <span className="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider">{app.category}</span>
            <h3 className="text-base font-bold text-white mt-0.5 hover:text-indigo-300 cursor-pointer" onClick={() => onSelect(app)}>
              {app.name}
            </h3>
            <div className="flex items-center space-x-2 mt-1 text-xs text-slate-400">
              <span>{app.developer}</span>
              {app.developer_verified ? (
                <span className="inline-flex items-center text-emerald-400 text-[10px] font-semibold">
                  <CheckCircle2 className="w-3 h-3 mr-0.5" /> Verified
                </span>
              ) : (
                <span className="inline-flex items-center text-amber-400 text-[10px] font-semibold">
                  <AlertTriangle className="w-3 h-3 mr-0.5" /> Unverified
                </span>
              )}
            </div>
          </div>

          {/* Risk Score Pill */}
          <div className="text-right">
            <div className={`px-2.5 py-1 rounded-xl text-xs font-bold font-mono tracking-tight ${getBadgeStyle(app.current_risk_level)}`}>
              {app.current_risk_score !== null ? `${app.current_risk_score}/100` : 'NOT SCANNED'}
            </div>
            <div className="text-[10px] font-bold uppercase tracking-wider mt-1 text-slate-400">
              {app.current_risk_level || 'UNKNOWN'}
            </div>
          </div>
        </div>

        {/* Purpose */}
        <p className="text-xs text-slate-300 leading-relaxed line-clamp-2 bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/50">
          "{app.declared_purpose}"
        </p>

        {/* App Meta Details */}
        <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
          <div className="flex items-center space-x-1">
            <Users className="w-3.5 h-3.5 text-slate-400" />
            <span>{app.user_count.toLocaleString()} Users</span>
          </div>
          <div className="flex items-center space-x-1">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span>{app.app_age_days} days old</span>
          </div>
          <div className="font-semibold text-slate-300">
            {app.requested_permissions.length} Scopes
          </div>
        </div>

        <div className="flex items-center justify-between border-t border-slate-800/80 pt-3">
          {getStatusBadge(app.status)}

          <button
            onClick={() => onSelect(app)}
            className="flex items-center space-x-1 text-xs font-bold text-indigo-400 hover:text-indigo-300"
          >
            <span>Analyze Report</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

      </div>

      {/* Card Quick Actions */}
      <div className="mt-4 pt-3 border-t border-slate-800/60 grid grid-cols-2 gap-2 text-xs">
        <button
          onClick={() => onOpenSimulator(app)}
          className="flex items-center justify-center space-x-1.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-indigo-600/30 text-slate-300 hover:text-indigo-300 border border-slate-700/50 transition-all"
        >
          <Sliders className="w-3.5 h-3.5" />
          <span>What-If</span>
        </button>
        <button
          onClick={() => onSelect(app)}
          className="flex items-center justify-center space-x-1.5 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 border border-indigo-500/30 font-medium transition-all"
        >
          <span>Inspect</span>
        </button>
      </div>
    </div>
  );
}
