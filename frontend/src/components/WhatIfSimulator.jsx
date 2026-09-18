import React, { useState, useEffect } from 'react';
import { Sliders, RefreshCw, AlertTriangle, ShieldCheck, ShieldAlert, ArrowRight, RotateCcw, Check, Sparkles } from 'lucide-react';
import { api } from '../services/api';

export default function WhatIfSimulator({ apps, initialAppId, onRefreshData }) {
  const [selectedAppId, setSelectedAppId] = useState(initialAppId || (apps.length > 0 ? apps[0].id : null));
  const [selectedApp, setSelectedApp] = useState(null);
  const [activePermissions, setActivePermissions] = useState([]);
  const [simulationResult, setSimulationResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (initialAppId) {
      setSelectedAppId(initialAppId);
    }
  }, [initialAppId]);

  useEffect(() => {
    if (selectedAppId && apps.length > 0) {
      const found = apps.find(a => a.id === Number(selectedAppId));
      if (found) {
        setSelectedApp(found);
        setActivePermissions([...found.requested_permissions]);
        runSimulation(found.id, [...found.requested_permissions]);
      }
    }
  }, [selectedAppId, apps]);

  const runSimulation = async (appId, perms) => {
    setLoading(true);
    try {
      const res = await api.simulatePermissions(appId, perms);
      setSimulationResult(res);
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTogglePermission = (perm) => {
    let updated;
    if (activePermissions.includes(perm)) {
      updated = activePermissions.filter(p => p !== perm);
    } else {
      updated = [...activePermissions, perm];
    }
    setActivePermissions(updated);
    if (selectedApp) {
      runSimulation(selectedApp.id, updated);
    }
  };

  const handleReset = () => {
    if (selectedApp) {
      setActivePermissions([...selectedApp.requested_permissions]);
      runSimulation(selectedApp.id, [...selectedApp.requested_permissions]);
    }
  };

  if (!apps || apps.length === 0) {
    return (
      <div className="p-8 glass-panel rounded-2xl text-center text-slate-400">
        No OAuth applications available for simulation.
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in">
      
      {/* Header & App Selector */}
      <div className="p-6 glass-panel rounded-2xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-400 font-extrabold text-xs uppercase tracking-wider">
            <Sparkles className="w-4 h-4" />
            <span>Interactive Risk Reduction Sandbox</span>
          </div>
          <h2 className="text-xl font-extrabold text-white mt-1">What-If Security Simulator</h2>
          <p className="text-xs text-slate-400 mt-1">
            Toggle off specific permission scopes to observe real-time risk reduction calculated by the hybrid risk engine.
          </p>
        </div>

        <div className="w-full md:w-72">
          <label className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            Select OAuth Application
          </label>
          <select
            value={selectedAppId || ''}
            onChange={(e) => setSelectedAppId(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs font-semibold text-white focus:outline-none focus:border-indigo-500"
          >
            {apps.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name} ({a.current_risk_level || 'ACTIVE'})
              </option>
            ))}
          </select>
        </div>
      </div>

      {selectedApp && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Column: Scope Toggles */}
          <div className="lg:col-span-7 glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="font-bold text-sm text-white">{selectedApp.name} Scopes</h3>
                <p className="text-xs text-slate-400">Declared Purpose: "{selectedApp.declared_purpose}"</p>
              </div>

              <button
                onClick={handleReset}
                className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-all"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset Scopes</span>
              </button>
            </div>

            <div className="space-y-2.5">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                Toggle Permission Access:
              </span>

              {selectedApp.requested_permissions.map((perm) => {
                const isEnabled = activePermissions.includes(perm);
                return (
                  <div
                    key={perm}
                    onClick={() => handleTogglePermission(perm)}
                    className={`p-3 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                      isEnabled
                        ? 'bg-slate-900/90 border-slate-700 hover:border-indigo-500/50'
                        : 'bg-rose-950/10 border-rose-500/20 opacity-60 hover:opacity-100'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div
                        className={`w-5 h-5 rounded-md flex items-center justify-center transition-all ${
                          isEnabled ? 'bg-indigo-600 text-white' : 'bg-slate-800 border border-slate-700 text-transparent'
                        }`}
                      >
                        <Check className="w-3.5 h-3.5" />
                      </div>
                      <span className={`font-mono text-xs font-bold ${isEnabled ? 'text-indigo-300' : 'text-slate-400 line-through'}`}>
                        {perm}
                      </span>
                    </div>

                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      isEnabled ? 'bg-indigo-500/10 text-indigo-400' : 'bg-rose-500/10 text-rose-400'
                    }`}>
                      {isEnabled ? 'ENABLED' : 'SIMULATED REMOVAL'}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column: Live Recalculated Risk Card */}
          <div className="lg:col-span-5 space-y-4">
            <div className="glass-panel p-6 rounded-2xl border border-indigo-500/30 bg-gradient-to-b from-indigo-950/30 to-slate-900/90 space-y-6">
              
              <div className="flex items-center justify-between border-b border-indigo-500/20 pb-3">
                <span className="text-xs font-bold text-indigo-300 uppercase tracking-wider">
                  Live Dynamic Recalculation
                </span>
                {loading && <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />}
              </div>

              {simulationResult ? (
                <div className="space-y-6">
                  
                  {/* Score Delta Display */}
                  <div className="grid grid-cols-2 gap-3 text-center">
                    <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
                      <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Baseline Risk</span>
                      <div className="text-2xl font-extrabold font-mono text-slate-200 mt-1">
                        {simulationResult.original_score}
                      </div>
                      <span className="text-[10px] text-slate-400">{simulationResult.original_level}</span>
                    </div>

                    <div className="p-3.5 rounded-xl bg-slate-900/80 border border-indigo-500/40">
                      <span className="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider block">Simulated Risk</span>
                      <div className="text-2xl font-extrabold font-mono text-indigo-300 mt-1">
                        {simulationResult.new_score}
                      </div>
                      <span className="text-[10px] text-indigo-400">{simulationResult.new_level}</span>
                    </div>
                  </div>

                  {/* Big Score Delta Pill */}
                  <div className={`p-4 rounded-xl text-center border font-mono ${
                    simulationResult.score_delta < 0
                      ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300'
                      : simulationResult.score_delta > 0
                      ? 'bg-rose-950/30 border-rose-500/40 text-rose-300'
                      : 'bg-slate-900 border-slate-800 text-slate-400'
                  }`}>
                    <div className="text-[11px] font-sans font-semibold uppercase tracking-wider">
                      Risk Delta Impact
                    </div>
                    <div className="text-3xl font-extrabold mt-1">
                      {simulationResult.score_delta < 0
                        ? `${simulationResult.score_delta} pts`
                        : simulationResult.score_delta > 0
                        ? `+${simulationResult.score_delta} pts`
                        : '0.0 pts'}
                    </div>
                  </div>

                  {/* Impact Summary */}
                  <div className="space-y-2 text-xs">
                    <span className="font-bold text-slate-300 uppercase text-[11px] tracking-wider block">
                      Simulation Findings:
                    </span>
                    <ul className="space-y-1 text-slate-400 text-[11px]">
                      {simulationResult.risk_factor_changes.map((change, i) => (
                        <li key={i} className="flex items-start space-x-1.5">
                          <span className="text-indigo-400 font-bold">•</span>
                          <span>{change}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                </div>
              ) : (
                <div className="py-8 text-center text-slate-400 text-xs">
                  Recalculating risk scores...
                </div>
              )}

            </div>
          </div>

        </div>
      )}

    </div>
  );
}
