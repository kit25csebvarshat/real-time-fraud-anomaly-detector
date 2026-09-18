import React, { useState, useEffect } from 'react';
import { Search, Filter, Plus, ShieldAlert, RefreshCw } from 'lucide-react';
import AppCard from '../components/AppCard';
import { api } from '../services/api';

export default function ApplicationsPage({ onSelectApp, onOpenSimulator, onOpenAddModal }) {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadApps();
  }, [statusFilter, search]);

  const loadApps = async () => {
    setLoading(true);
    try {
      const data = await api.getApps(statusFilter, search);
      setApps(data);
    } catch (err) {
      console.error('Failed to load apps:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in">
      
      {/* Search & Filter Header */}
      <div className="p-5 glass-panel rounded-2xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-extrabold text-white flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-indigo-400" />
            <span>OAuth Applications Catalog</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Discover, inspect, and analyze third-party applications connected to employee accounts.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search app or developer..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="TRUSTED">Trusted</option>
            <option value="REVIEW">Review Required</option>
            <option value="REVOKED">Revoked</option>
          </select>

          <button
            onClick={onOpenAddModal}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md shadow-indigo-600/20"
          >
            <Plus className="w-4 h-4" />
            <span>New App</span>
          </button>
        </div>
      </div>

      {/* Apps Grid */}
      {loading ? (
        <div className="py-20 text-center space-y-2 text-slate-400 text-xs">
          <RefreshCw className="w-6 h-6 animate-spin text-indigo-500 mx-auto" />
          <p>Loading application catalog...</p>
        </div>
      ) : apps.length === 0 ? (
        <div className="py-16 text-center glass-panel rounded-2xl text-slate-400 text-xs">
          No OAuth applications match the selected search criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {apps.map((app) => (
            <AppCard
              key={app.id}
              app={app}
              onSelect={onSelectApp}
              onOpenSimulator={onOpenSimulator}
            />
          ))}
        </div>
      )}

    </div>
  );
}
