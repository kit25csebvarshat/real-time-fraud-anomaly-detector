import React from 'react';
import { Shield, Plus, Sparkles, User, RefreshCw, AlertTriangle } from 'lucide-react';

export default function Navbar({ onOpenAddModal, activeTab, setActiveTab }) {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 bg-[#0B0F17]/80 backdrop-blur-md">
      <div className="px-4 lg:px-8 py-3.5 flex items-center justify-between">
        
        {/* Logo & Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 p-[1px] shadow-lg shadow-indigo-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[11px] flex items-center justify-center">
              <Shield className="w-5 h-5 text-indigo-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-200 bg-clip-text text-transparent">
                OAuthGuard
              </h1>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                AI Platform
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">OAuth Risk & Permission Intelligence</p>
          </div>
        </div>

        {/* Center Live Intelligence Badge */}
        <div className="hidden md:flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-xs text-slate-300">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="font-medium text-slate-300">Simulated OAuth Environment Active</span>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenAddModal}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white text-xs font-semibold shadow-lg shadow-indigo-600/25 transition-all duration-150 active:scale-95"
          >
            <Plus className="w-4 h-4" />
            <span>Add OAuth App</span>
          </button>

          {/* User Profile Pill */}
          <div className="flex items-center space-x-2 pl-3 border-l border-slate-800">
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
              <User className="w-4 h-4" />
            </div>
            <div className="hidden xl:block text-left">
              <div className="text-xs font-semibold text-slate-200">Security Admin</div>
              <div className="text-[10px] text-slate-400">admin@oauthguard.io</div>
            </div>
          </div>
        </div>

      </div>
    </header>
  );
}
