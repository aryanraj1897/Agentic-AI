import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import { checkHealth } from './services/api';

export function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  const verifyConnection = async () => {
    setLoading(true);
    const result = await checkHealth();
    setIsConnected(result.success);
    setLoading(false);
  };

  useEffect(() => {
    verifyConnection();
  }, []);

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans">
      <Header isConnected={isConnected} loading={loading} onRetry={verifyConnection} />
      <main className="flex-1">
        <Dashboard />
      </main>
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500 bg-[#070a12]">
        Autonomous Data Analysis Agent • Phase 1 Core Infrastructure
      </footer>
    </div>
  );
}

export default App;
