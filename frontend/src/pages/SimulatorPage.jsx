import React, { useState, useEffect } from 'react';
import WhatIfSimulator from '../components/WhatIfSimulator';
import { api } from '../services/api';

export default function SimulatorPage({ initialAppId }) {
  const [apps, setApps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadApps();
  }, []);

  const loadApps = async () => {
    try {
      const data = await api.getApps();
      setApps(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-slate-400 text-xs">Loading simulator...</div>;

  return <WhatIfSimulator apps={apps} initialAppId={initialAppId} onRefreshData={loadApps} />;
}
