import React, { useState, useEffect } from 'react';
import { X, ShieldAlert, ShieldCheck, AlertTriangle, RefreshCw, CheckCircle2, Sliders, Lock, ArrowRight, Activity } from 'lucide-react';
import { api } from '../services/api';

export default function AppDetailModal({ app, onClose, onRefreshData, onOpenSimulator }) {
  const [scan, setScan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [actionMessage, setActionMessage] = useState('');

  useEffect(() => {
    if (app) {
      loadScanDetails();
    }
  }, [app]);

  const loadScanDetails = async () => {
    setLoading(true);
    try {
      const data = await api.getAppRisk(app.id);
      setScan(data);
    } catch (err) {
      console.error('Failed to load risk details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRescan = async () => {
    setScanning(true);
    try {
      const freshScan = await api.scanApp(app.id);
      setScan(freshScan);
      setActionMessage('Fresh security scan completed successfully!');
      onRefreshData();
      setTimeout(() => setActionMessage(''), 4000);
    } catch (err) {
      console.error('Failed to rescan:', err);
    } finally {
      setScanning(false);
    }
  };

  const handleTrust = async () => {
    try {
      await api.markTrusted(app.id, 'Administrator approved application after permission review');
      setActionMessage('Application marked as TRUSTED. Audit event logged.');
      onRefreshData();
      setTimeout(() => setActionMessage(''), 4000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleReview = async () => {
    try {
      await api.markReview(app.id, 'Administrator requested secondary security review');
      setActionMessage('Application marked for REVIEW. Audit event logged.');
      onRefreshData();
      setTimeout(() => setActionMessage(''), 4000);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRevoke = async () => {
    try {
      await api.revokeAccess(app.id, 'SIMULATED ACTION: Access revoked by administrator');
      setActionMessage('SIMULATED ACTION: Access revoked. Audit event logged.');
      onRefreshData();
      setTimeout(() => setActionMessage(''), 4000);
    } catch (err) {
      console.error(err);
    }
  };

  if (!app) return null;

  const getRelevanceBadge = (rel) => {
    switch (rel) {
      case 'HIGH_RISK_MISMATCH':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">HIGH-RISK MISMATCH</span>;
      case 'POTENTIALLY_EXCESSIVE':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">POTENTIALLY EXCESSIVE</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">RELEVANT</span>;
    }
  };

  const getSensitivityBadge = (sens) => {
    switch (sens) {
      case 'CRITICAL':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold badge-critical">CRITICAL</span>;
      case 'HIGH':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold badge-high">HIGH</span>;
      case 'MEDIUM':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold badge-medium">MEDIUM</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold badge-low">LOW</span>;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-4xl glass-panel rounded-2xl border border-slate-700/80 shadow-2xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-extrabold text-lg">
              {app.name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-extrabold text-white">{app.name}</h2>
                <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">{app.category}</span>
              </div>
              <p className="text-xs text-slate-400">Developer: <strong className="text-slate-200">{app.developer}</strong> {app.developer_verified ? ' (Verified)' : ' (Unverified)'}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleRescan}
              disabled={scanning}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-all border border-slate-700"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${scanning ? 'animate-spin text-indigo-400' : ''}`} />
              <span>{scanning ? 'Scanning...' : 'Re-scan'}</span>
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-200">
          
          {actionMessage && (
            <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 font-semibold flex items-center justify-between animate-in fade-in">
              <span>{actionMessage}</span>
            </div>
          )}

          {loading ? (
            <div className="py-12 text-center space-y-3">
              <RefreshCw className="w-8 h-8 animate-spin text-indigo-500 mx-auto" />
              <p className="text-slate-400">Analyzing Permission-Purpose Intelligence & ML Risk Model...</p>
            </div>
          ) : scan ? (
            <>
              {/* Risk Summary Banner */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                
                {/* Overall Score Box */}
                <div className="p-5 rounded-2xl glass-card border border-slate-800 flex flex-col justify-between">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Hybrid Risk Assessment</span>
                  <div className="my-2">
                    <div className="text-4xl font-extrabold font-mono tracking-tight text-white">
                      {scan.final_score} <span className="text-sm font-normal text-slate-400">/ 100</span>
                    </div>
                    <div className="mt-2">
                      <span className={`px-3 py-1 rounded-lg text-xs font-extrabold tracking-wider ${
                        scan.risk_level === 'CRITICAL' ? 'badge-critical' :
                        scan.risk_level === 'HIGH' ? 'badge-high' :
                        scan.risk_level === 'MEDIUM' ? 'badge-medium' : 'badge-low'
                      }`}>
                        {scan.risk_level} RISK
                      </span>
                    </div>
                  </div>
                  <div className="text-[11px] text-slate-400 border-t border-slate-800/80 pt-2 flex justify-between">
                    <span>Status: <strong className="text-white">{app.status}</strong></span>
                    <span>Scanned: {new Date(scan.scanned_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                </div>

                {/* Score Breakdown (Rule vs ML) */}
                <div className="p-5 rounded-2xl glass-card border border-slate-800 md:col-span-2 space-y-4">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Risk Engine Weighting</span>
                  
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-300 font-semibold">Rule-Based Engine Score (60% Weight)</span>
                        <span className="font-mono font-bold text-amber-400">{scan.rule_score} / 100</span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                        <div className="h-full bg-amber-500 rounded-full" style={{ width: `${scan.rule_score}%` }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-300 font-semibold">RandomForest ML Classifier (40% Weight)</span>
                        <span className="font-mono font-bold text-purple-400">{scan.ml_score} / 100</span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                        <div className="h-full bg-purple-500 rounded-full" style={{ width: `${scan.ml_score}%` }}></div>
                      </div>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-400 italic">
                    Note: Score combines rule interpretability with machine-learning pattern recognition across 17 security vectors.
                  </p>
                </div>

              </div>

              {/* Primary Risk Factors */}
              {scan.major_risk_factors && scan.major_risk_factors.length > 0 && (
                <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-500/30 space-y-2.5">
                  <h4 className="font-extrabold text-xs text-purple-300 uppercase tracking-wider flex items-center space-x-1.5">
                    <ShieldAlert className="w-4 h-4 text-purple-400" />
                    <span>Primary Identified Risk Factors ({scan.major_risk_factors.length})</span>
                  </h4>
                  <ul className="space-y-1.5 pl-2 text-slate-300">
                    {scan.major_risk_factors.map((factor, i) => (
                      <li key={i} className="flex items-start space-x-2">
                        <span className="text-purple-400 font-bold">•</span>
                        <span>{factor}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Permission-Purpose Intelligence Matrix */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-extrabold text-xs uppercase tracking-wider text-slate-300">
                    Permission Scope Intelligence Breakdown
                  </h4>
                  <span className="text-[11px] text-slate-400">{scan.permissions_breakdown.length} Requested Scopes</span>
                </div>

                <div className="border border-slate-800 rounded-xl overflow-hidden glass-panel">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-slate-900/80 border-b border-slate-800 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                        <th className="py-2.5 px-4">Permission Scope</th>
                        <th className="py-2.5 px-4">Category</th>
                        <th className="py-2.5 px-4">Sensitivity</th>
                        <th className="py-2.5 px-4">Purpose Relevance</th>
                        <th className="py-2.5 px-4">Description</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 text-xs">
                      {scan.permissions_breakdown.map((item, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                          <td className="py-2.5 px-4 font-mono text-indigo-300 font-bold">{item.permission}</td>
                          <td className="py-2.5 px-4 capitalize text-slate-300">{item.category}</td>
                          <td className="py-2.5 px-4">{getSensitivityBadge(item.sensitivity)}</td>
                          <td className="py-2.5 px-4">{getRelevanceBadge(item.purpose_relevance)}</td>
                          <td className="py-2.5 px-4 text-slate-400 text-[11px]">{item.description}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Suspicious Combinations Section */}
              {scan.suspicious_combinations && scan.suspicious_combinations.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-extrabold text-xs uppercase tracking-wider text-amber-400 flex items-center space-x-1.5">
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                    <span>Suspicious Permission Combinations Detected</span>
                  </h4>
                  <div className="space-y-2">
                    {scan.suspicious_combinations.map((combo, i) => (
                      <div key={i} className="p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 text-xs space-y-1">
                        <div className="flex items-center justify-between font-bold text-amber-300">
                          <span>{combo.title}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 border border-amber-500/40 text-amber-300 font-mono">
                            {combo.combination.join(' + ')}
                          </span>
                        </div>
                        <p className="text-slate-300 text-[11px] leading-relaxed">{combo.explanation}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Potential Impact & Recommended Action */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div className="p-4 rounded-xl glass-card border border-slate-800 space-y-2">
                  <h5 className="font-extrabold text-xs text-rose-400 uppercase tracking-wider">Potential Security Impact</h5>
                  <p className="text-slate-300 text-xs leading-relaxed">{scan.potential_impact}</p>
                </div>
                
                <div className="p-4 rounded-xl glass-card border border-slate-800 space-y-2">
                  <h5 className="font-extrabold text-xs text-emerald-400 uppercase tracking-wider">Recommended Security Action</h5>
                  <div className="text-slate-300 text-xs leading-relaxed whitespace-pre-line">{scan.recommended_action}</div>
                </div>
              </div>

            </>
          ) : null}

        </div>

        {/* Modal Action Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-900/90 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => {
                onClose();
                onOpenSimulator(app);
              }}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/40 text-xs font-semibold transition-all"
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>Launch What-If Simulator</span>
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleTrust}
              className="px-3 py-2 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-300 border border-emerald-500/30 text-xs font-semibold transition-all"
            >
              Mark Trusted
            </button>

            <button
              onClick={handleReview}
              className="px-3 py-2 rounded-xl bg-amber-600/20 hover:bg-amber-600/40 text-amber-300 border border-amber-500/30 text-xs font-semibold transition-all"
            >
              Mark for Review
            </button>

            <button
              onClick={handleRevoke}
              className="px-3.5 py-2 rounded-xl bg-rose-600/80 hover:bg-rose-600 text-white text-xs font-bold shadow-md shadow-rose-600/20 transition-all"
            >
              Simulate Revocation
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
