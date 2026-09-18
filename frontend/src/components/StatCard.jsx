import React from 'react';

export default function StatCard({ title, value, subtext, icon: Icon, colorClass, borderClass }) {
  return (
    <div className={`p-5 rounded-2xl glass-panel border ${borderClass || 'border-slate-800'} relative overflow-hidden transition-all duration-200 hover:border-slate-700`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl font-extrabold text-white mt-1.5 tracking-tight font-mono">{value}</h3>
          {subtext && <p className="text-[11px] text-slate-400 mt-1">{subtext}</p>}
        </div>
        <div className={`p-3 rounded-xl ${colorClass}`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
      </div>
    </div>
  );
}
