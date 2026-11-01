import React from 'react';
import { Lightbulb, CheckCircle2 } from 'lucide-react';

export const Insights = ({ insights }) => {
  if (!insights || insights.length === 0) return null;

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-4">
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
        <Lightbulb className="w-5 h-5 text-amber-400" />
        <h4 className="font-bold text-white text-sm">Automated Data Insights ({insights.length})</h4>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {insights.map((insight, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-3 text-xs text-slate-300 hover:border-slate-700 transition-colors"
          >
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <span className="leading-relaxed">{insight}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Insights;
