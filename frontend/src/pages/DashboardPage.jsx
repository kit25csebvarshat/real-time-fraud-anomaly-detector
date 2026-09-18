import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, AlertTriangle, ShieldCheck, Activity, Users, ArrowUpRight, Sparkles, RefreshCw } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import StatCard from '../components/StatCard';
import AppCard from '../components/AppCard';
import { api } from '../services/api';

export default function DashboardPage({ onSelectApp, onOpenSimulator, setActiveTab }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoading(true);
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center space-y-3">
        <RefreshCw className="w-8 h-8 animate-spin text-indigo-500 mx-auto" />
        <p className="text-slate-400 text-xs font-semibold">Aggregating OAuth Risk & Permission Intelligence...</p>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="space-y-6 animate-in fade-in">
      
      {/* Top Welcome & KPI Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-400 text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-4 h-4" />
            <span>Security Intelligence Center</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white mt-1 tracking-tight">OAuth Application Risk Dashboard</h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time permission-purpose intelligence across {stats.total_apps} connected enterprise OAuth applications.
          </p>
        </div>

        <button
          onClick={loadStats}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-all self-start md:self-auto"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* KPI Stat Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total OAuth Apps"
          value={stats.total_apps}
          subtext="Connected enterprise apps"
          icon={Shield}
          colorClass="bg-indigo-600/30 border border-indigo-500/30"
          borderClass="border-slate-800"
        />
        <StatCard
          title="Critical Risk Apps"
          value={stats.critical_risk_count}
          subtext="Requires immediate mitigation"
          icon={ShieldAlert}
          colorClass="bg-purple-600/30 border border-purple-500/30"
          borderClass="border-purple-500/30"
        />
        <StatCard
          title="High Risk Apps"
          value={stats.high_risk_count}
          subtext="Excessive permissions"
          icon={AlertTriangle}
          colorClass="bg-rose-600/30 border border-rose-500/30"
          borderClass="border-rose-500/30"
        />
        <StatCard
          title="Apps Needing Review"
          value={stats.apps_requiring_review}
          subtext="Flagged by security team"
          icon={Activity}
          colorClass="bg-amber-600/30 border border-amber-500/30"
          borderClass="border-amber-500/30"
        />
      </div>

      {/* Recharts Data Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Risk Distribution Donut Chart */}
        <div className="lg:col-span-5 glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-300 mb-2">
            Risk Classification Distribution
          </h3>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats.risk_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {stats.risk_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '12px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-800">
            {stats.risk_distribution.map((item, idx) => (
              <div key={idx} className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                <span className="text-slate-400">{item.name}:</span>
                <span className="font-mono font-bold text-white">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Permission Category Distribution Bar Chart */}
        <div className="lg:col-span-7 glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-300 mb-2">
            Requested Permission Scope Categories
          </h3>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.permission_category_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="category" stroke="#9CA3AF" fontSize={11} tickLine={false} />
                <YAxis stroke="#9CA3AF" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '12px', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#6366F1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <p className="text-[11px] text-slate-400 italic text-center border-t border-slate-800 pt-2">
            Higher drive and email permissions represent elevated data exfiltration vectors.
          </p>
        </div>

      </div>

      {/* Top High-Risk Applications Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-extrabold text-white uppercase tracking-wider">Top High-Risk OAuth Applications</h3>
            <p className="text-xs text-slate-400">Applications requesting excessive permissions relative to declared purpose</p>
          </div>
          <button
            onClick={() => setActiveTab('apps')}
            className="flex items-center space-x-1 text-xs font-bold text-indigo-400 hover:text-indigo-300"
          >
            <span>View All ({stats.total_apps})</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {stats.top_risk_apps.map((app) => (
            <AppCard
              key={app.id}
              app={{
                ...app,
                requested_permissions: Array(app.requested_permissions_count).fill('scope'),
                declared_purpose: app.name === 'DocuFlow AI' ? 'AI-powered document organization and PDF conversion platform for employees.' : 'OAuth application requesting sensitive enterprise permissions.',
                app_age_days: app.name === 'DocuFlow AI' ? 18 : 30,
                user_count: app.name === 'DocuFlow AI' ? 342 : 500,
                developer_verified: false,
                current_risk_score: app.risk_score,
                current_risk_level: app.risk_level
              }}
              onSelect={onSelectApp}
              onOpenSimulator={onOpenSimulator}
            />
          ))}
        </div>
      </div>

    </div>
  );
}
