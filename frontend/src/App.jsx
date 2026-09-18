import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import ApplicationsPage from './pages/ApplicationsPage';
import SimulatorPage from './pages/SimulatorPage';
import AuditLogsPage from './pages/AuditLogsPage';
import AppDetailModal from './components/AppDetailModal';
import AddAppModal from './components/AddAppModal';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedApp, setSelectedApp] = useState(null);
  const [simulatorAppId, setSimulatorAppId] = useState(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleOpenSimulator = (app) => {
    setSimulatorAppId(app.id);
    setActiveTab('simulator');
  };

  const handleRefreshData = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] text-slate-100 flex flex-col font-['Plus_Jakarta_Sans',sans-serif]">
      {/* Top Navbar */}
      <Navbar
        onOpenAddModal={() => setIsAddModalOpen(true)}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      <div className="flex-1 flex w-full">
        {/* Left Sidebar */}
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Main Content Area */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full overflow-x-hidden">
          {activeTab === 'dashboard' && (
            <DashboardPage
              key={refreshTrigger}
              onSelectApp={setSelectedApp}
              onOpenSimulator={handleOpenSimulator}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === 'apps' && (
            <ApplicationsPage
              key={refreshTrigger}
              onSelectApp={setSelectedApp}
              onOpenSimulator={handleOpenSimulator}
              onOpenAddModal={() => setIsAddModalOpen(true)}
            />
          )}

          {activeTab === 'simulator' && (
            <SimulatorPage
              key={refreshTrigger}
              initialAppId={simulatorAppId}
            />
          )}

          {activeTab === 'audit' && (
            <AuditLogsPage key={refreshTrigger} />
          )}
        </main>
      </div>

      {/* App Detail Scan Report Modal */}
      <AppDetailModal
        app={selectedApp}
        onClose={() => setSelectedApp(null)}
        onRefreshData={handleRefreshData}
        onOpenSimulator={handleOpenSimulator}
      />

      {/* Register New App Modal */}
      <AddAppModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onAppCreated={handleRefreshData}
      />
    </div>
  );
}
