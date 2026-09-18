import React from 'react';
import { LayoutDashboard, ShieldAlert, Sliders, History, Sparkles, BookOpen } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, badge: null },
    { id: 'apps', label: 'OAuth Apps Catalog', icon: ShieldAlert, badge: '10' },
    { id: 'simulator', label: 'What-If Simulator', icon: Sliders, badge: 'Live' },
    { id: 'audit', label: 'Security Audit Trail', icon: History, badge: null },
  ];

  return (
    <aside className="w-64 shrink-0 glass-panel border-r border-slate-800/80 min-h-[calc(100vh-65px)] p-4 flex flex-col justify-between hidden md:flex">
      <div className="space-y-6">
        <div>
          <div className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-3">
            Main Navigation
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 ${
                    isActive
                      ? 'bg-gradient-to-r from-indigo-600/90 to-indigo-700/80 text-white shadow-md shadow-indigo-600/20 border border-indigo-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        isActive
                          ? 'bg-white/20 text-white'
                          : item.badge === 'Live'
                          ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Feature Highlight Box */}
        <div className="p-4 rounded-xl bg-gradient-to-b from-indigo-950/40 to-slate-900/80 border border-indigo-500/20 text-xs space-y-2">
          <div className="flex items-center space-x-2 text-indigo-400 font-bold">
            <Sparkles className="w-4 h-4" />
            <span>Permission Intelligence</span>
          </div>
          <p className="text-slate-400 text-[11px] leading-relaxed">
            Evaluates requested permissions against declared app purposes to identify excessive data access.
          </p>
        </div>
      </div>

      {/* Footer Info */}
      <div className="pt-4 border-t border-slate-800/80 text-[11px] text-slate-400 space-y-1">
        <div className="flex items-center justify-between">
          <span>Engine Weight:</span>
          <span className="font-mono text-indigo-400 font-semibold">60% Rule / 40% ML</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Model:</span>
          <span className="font-mono text-emerald-400 font-semibold">RandomForest (96.5%)</span>
        </div>
      </div>
    </aside>
  );
}
