import React, { useState } from 'react';
import { X, Plus, Shield, Check, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

const AVAILABLE_SCOPES = [
  { scope: 'profile.read', category: 'Profile', sens: 'LOW' },
  { scope: 'basic_identity.read', category: 'Profile', sens: 'LOW' },
  { scope: 'calendar.read', category: 'Calendar', sens: 'MEDIUM' },
  { scope: 'calendar.write', category: 'Calendar', sens: 'HIGH' },
  { scope: 'contacts.read', category: 'Contacts', sens: 'MEDIUM' },
  { scope: 'contacts.write', category: 'Contacts', sens: 'HIGH' },
  { scope: 'drive.read', category: 'Drive', sens: 'MEDIUM' },
  { scope: 'drive.write', category: 'Drive', sens: 'HIGH' },
  { scope: 'gmail.read', category: 'Email', sens: 'HIGH' },
  { scope: 'gmail.send', category: 'Email', sens: 'CRITICAL' },
  { scope: 'admin.access', category: 'Admin', sens: 'CRITICAL' },
  { scope: 'user.impersonation', category: 'Admin', sens: 'CRITICAL' },
];

export default function AddAppModal({ isOpen, onClose, onAppCreated }) {
  const [name, setName] = useState('');
  const [developer, setDeveloper] = useState('');
  const [developerVerified, setDeveloperVerified] = useState(false);
  const [declaredPurpose, setDeclaredPurpose] = useState('');
  const [category, setCategory] = useState('Productivity');
  const [appAgeDays, setAppAgeDays] = useState(30);
  const [userCount, setUserCount] = useState(500);
  const [selectedPermissions, setSelectedPermissions] = useState(['profile.read']);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const toggleScope = (scope) => {
    if (selectedPermissions.includes(scope)) {
      setSelectedPermissions(selectedPermissions.filter(s => s !== scope));
    } else {
      setSelectedPermissions([...selectedPermissions, scope]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !developer || !declaredPurpose) {
      setError('Please fill out all required fields.');
      return;
    }
    if (selectedPermissions.length === 0) {
      setError('Please select at least one permission scope.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await api.createApp({
        name,
        developer,
        developer_verified: developerVerified,
        declared_purpose: declaredPurpose,
        category,
        app_age_days: Number(appAgeDays),
        user_count: Number(userCount),
        requested_permissions: selectedPermissions,
      });

      onAppCreated();
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to add application');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-2xl glass-panel rounded-2xl border border-slate-700 shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
          <div className="flex items-center space-x-2 text-white font-extrabold text-base">
            <Shield className="w-5 h-5 text-indigo-400" />
            <span>Register New OAuth Application</span>
          </div>
          <button onClick={onClose} className="p-1 rounded bg-slate-800 text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs text-slate-200 max-h-[80vh] overflow-y-auto">
          {error && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 font-semibold">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-400 font-semibold uppercase tracking-wider mb-1">App Name *</label>
              <input
                type="text"
                placeholder="e.g. DocuFlow AI"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-semibold uppercase tracking-wider mb-1">Developer Name *</label>
              <input
                type="text"
                placeholder="e.g. DocuFlow Technologies"
                value={developer}
                onChange={(e) => setDeveloper(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-400 font-semibold uppercase tracking-wider mb-1">Declared App Purpose *</label>
            <textarea
              rows="2"
              placeholder="e.g. AI-powered document organization and PDF conversion platform for employees."
              value={declaredPurpose}
              onChange={(e) => setDeclaredPurpose(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-slate-400 font-semibold uppercase tracking-wider mb-1">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none"
              >
                <option value="PDF Document Converter">PDF Document Converter</option>
                <option value="Calendar Scheduling Assistant">Calendar Scheduling Assistant</option>
                <option value="AI Email Assistant">AI Email Assistant</option>
                <option value="Company Backup Utility">Company Backup Utility</option>
                <option value="Meeting Transcription Tool">Meeting Transcription Tool</option>
                <option value="CRM Connector">CRM Connector</option>
                <option value="Document Signing Platform">Document Signing Platform</option>
                <option value="Social Media Scheduler">Social Media Scheduler</option>
                <option value="Productivity">Productivity</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 font-semibold uppercase tracking-wider mb-1">App Age (Days)</label>
              <input
                type="number"
                value={appAgeDays}
                onChange={(e) => setAppAgeDays(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-400 font-semibold uppercase tracking-wider mb-1">User Count</label>
              <input
                type="number"
                value={userCount}
                onChange={(e) => setUserCount(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none"
              />
            </div>
          </div>

          <div className="flex items-center space-x-2 pt-1">
            <input
              type="checkbox"
              id="dev_verify"
              checked={developerVerified}
              onChange={(e) => setDeveloperVerified(e.target.checked)}
              className="w-4 h-4 rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-0"
            />
            <label htmlFor="dev_verify" className="text-slate-300 font-semibold cursor-pointer">
              Developer Verified Status
            </label>
          </div>

          <div>
            <label className="block text-slate-400 font-semibold uppercase tracking-wider mb-2">
              Select Requested Permission Scopes
            </label>
            <div className="grid grid-cols-2 gap-2">
              {AVAILABLE_SCOPES.map((item) => {
                const isSelected = selectedPermissions.includes(item.scope);
                return (
                  <div
                    key={item.scope}
                    onClick={() => toggleScope(item.scope)}
                    className={`p-2.5 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-indigo-950/40 border-indigo-500/50 text-indigo-300'
                        : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <div className={`w-4 h-4 rounded border flex items-center justify-center ${
                        isSelected ? 'bg-indigo-600 border-indigo-500 text-white' : 'border-slate-700'
                      }`}>
                        {isSelected && <Check className="w-3 h-3" />}
                      </div>
                      <span className="font-mono font-bold text-xs">{item.scope}</span>
                    </div>
                    <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                      {item.sens}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center space-x-1.5 px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold shadow-lg shadow-indigo-600/30"
            >
              {submitting && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
              <span>{submitting ? 'Scanning & Registering...' : 'Register & Scan App'}</span>
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}
