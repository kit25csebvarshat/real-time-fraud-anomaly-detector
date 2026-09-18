import React, { useState, useEffect } from 'react';
import { History, Search, Filter, ShieldCheck, ShieldAlert, Sliders, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export default function AuditLogTable() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState('');

  useEffect(() => {
    loadAuditLogs();
  }, [actionFilter, search]);

  const loadAuditLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs(actionFilter, search);
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const getActionBadge = (action) => {
    switch (action) {
      case 'MARK_TRUSTED':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">MARK TRUSTED</span>;
      case 'MARK_REVIEW':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">FLAG REVIEW</span>;
      case 'REVOKE_ACCESS':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">REVOKE ACCESS</span>;
      case 'PERMISSION_SIMULATION':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">WHAT-IF SIMULATION</span>;
      case 'ADD_APP':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">REGISTER APP</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">SECURITY SCAN</span>;
    }
  };

  return (
    <div className="space-y-4 animate-in fade-in">
      
      {/* Controls Header */}
      <div className="p-5 glass-panel rounded-2xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-extrabold text-white flex items-center space-x-2">
            <History className="w-5 h-5 text-indigo-400" />
            <span>Security Audit Trail</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Immutable event record of all administrator trust overrides, access revocations, and simulations.
          </p>
        </div>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          <div className="relative w-full md:w-60">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search app or reason..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none"
          >
            <option value="">All Actions</option>
            <option value="MARK_TRUSTED">Mark Trusted</option>
            <option value="MARK_REVIEW">Flag Review</option>
            <option value="REVOKE_ACCESS">Revoke Access</option>
            <option value="PERMISSION_SIMULATION">Simulation</option>
            <option value="ADD_APP">Register App</option>
            <option value="INITIAL_SCAN">Initial Scan</option>
          </select>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        {loading ? (
          <div className="py-12 text-center text-slate-400 text-xs flex items-center justify-center space-x-2">
            <RefreshCw className="w-4 h-4 animate-spin text-indigo-500" />
            <span>Loading security audit trail...</span>
          </div>
        ) : logs.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-xs">
            No audit log records found.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-900/90 border-b border-slate-800 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Administrator</th>
                  <th className="py-3 px-4">Application</th>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Risk Delta</th>
                  <th className="py-3 px-4">Reason / Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4 font-mono text-slate-400 text-[11px]">
                      {new Date(log.timestamp).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </td>
                    <td className="py-3 px-4 font-medium text-slate-200">{log.user_email}</td>
                    <td className="py-3 px-4 font-bold text-white">{log.app_name}</td>
                    <td className="py-3 px-4">{getActionBadge(log.action)}</td>
                    <td className="py-3 px-4 font-mono font-semibold">
                      {log.previous_risk !== null && log.current_risk !== null ? (
                        <span>
                          {log.previous_risk} → <strong className="text-indigo-300">{log.current_risk}</strong>
                        </span>
                      ) : log.current_risk !== null ? (
                        <strong className="text-indigo-300">{log.current_risk}</strong>
                      ) : (
                        <span className="text-slate-500">-</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px] max-w-md truncate">{log.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}
