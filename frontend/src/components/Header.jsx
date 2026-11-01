import React from 'react';
import { Bot, Layers, Sparkles } from 'lucide-react';
import HealthBadge from './HealthBadge';

export const Header = ({ isConnected, loading, onRetry }) => {
  return (
    <header className="border-b border-slate-800 bg-[#0c121e]/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/20">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-lg text-white tracking-tight">
                Autonomous Data Analysis Agent
              </h1>
              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-950 text-blue-300 border border-blue-800/60 font-mono">
                Phase 1
              </span>
            </div>
            <p className="text-xs text-slate-400">
              AI-Driven Dataset Analysis & Insights Platform
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <HealthBadge isConnected={isConnected} loading={loading} onRetry={onRetry} />
        </div>
      </div>
    </header>
  );
};

export default Header;
