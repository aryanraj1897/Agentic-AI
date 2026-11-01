import React from 'react';
import { Activity, RefreshCw } from 'lucide-react';

export const HealthBadge = ({ isConnected, loading, onRetry }) => {
  if (loading) {
    return (
      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700 text-slate-300 text-sm font-medium">
        <RefreshCw className="w-4 h-4 animate-spin text-blue-400" />
        <span>Checking backend connection...</span>
      </div>
    );
  }

  if (isConnected) {
    return (
      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 text-sm font-medium shadow-lg shadow-emerald-950/20">
        <span className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
        </span>
        <span>Backend Connected ✓</span>
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-rose-950/60 border border-rose-500/30 text-rose-300 text-sm font-medium shadow-lg shadow-rose-950/20">
      <span className="h-2.5 w-2.5 rounded-full bg-rose-500"></span>
      <span>Backend Disconnected</span>
      {onRetry && (
        <button
          onClick={onRetry}
          title="Retry Connection"
          className="ml-1 p-0.5 hover:bg-rose-900/50 rounded transition-colors text-rose-200"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
};

export default HealthBadge;
