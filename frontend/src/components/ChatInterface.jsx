import React, { useState } from 'react';
import { Sparkles, Send, HelpCircle } from 'lucide-react';

export const ChatInterface = ({ onRunAnalysis, loading, datasetId }) => {
  const [query, setQuery] = useState('Analyze sales performance and identify the best-performing products and regions.');

  const sampleQueries = [
    'Analyze sales performance and identify top products.',
    'Show monthly sales trends and aggregations.',
    'Identify regional sales performance and outliers.',
    'Find highest revenue department and compare distributions.',
  ];

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!query.trim() || loading || !datasetId) return;
    onRunAnalysis(query);
  };

  const handleChipClick = (q) => {
    setQuery(q);
    if (!loading && datasetId) {
      onRunAnalysis(q);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-4">
      <div>
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-blue-400" />
          Autonomous Analysis Workspace
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Ask questions in plain English. The LangGraph agent orchestrates profiling, intent classification, planning, AST validation, execution, self-healing code repair, chart visualization, insight extraction, and executive reporting.
        </p>
      </div>

      {/* Recommended Query Chips */}
      <div className="space-y-1.5">
        <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
          <HelpCircle className="w-3.5 h-3.5 text-blue-400" />
          Suggested Sample Queries:
        </span>
        <div className="flex gap-2 flex-wrap">
          {sampleQueries.map((q, idx) => (
            <button
              key={idx}
              type="button"
              disabled={loading || !datasetId}
              onClick={() => handleChipClick(q)}
              className="text-xs px-3 py-1.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 text-blue-300 border border-slate-700/80 transition-all cursor-pointer disabled:opacity-50"
            >
              "{q}"
            </button>
          ))}
        </div>
      </div>

      {/* Query Submission Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading || !datasetId}
          placeholder={datasetId ? "Ask a question about your dataset..." : "Upload a dataset above to start analysis..."}
          className="flex-1 bg-slate-950 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-sans transition-colors disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !query.trim() || !datasetId}
          className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2 shrink-0 disabled:opacity-50 cursor-pointer"
        >
          <Send className="w-4 h-4" />
          <span>{loading ? 'Executing Agent Graph...' : 'Start Analysis'}</span>
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
