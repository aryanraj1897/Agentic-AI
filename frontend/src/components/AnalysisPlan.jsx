import React from 'react';
import { Target, ListOrdered, Layers } from 'lucide-react';

export const AnalysisPlan = ({ intent, plan }) => {
  if (!intent && (!plan || plan.length === 0)) return null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Intent Analysis */}
      <div className="glass-card rounded-2xl p-6 space-y-4 border border-slate-800">
        <div className="flex items-center gap-2 text-blue-400 font-bold text-sm border-b border-slate-800 pb-3">
          <Target className="w-4 h-4" />
          <span>Intent Classification & Objective</span>
        </div>

        {intent && (
          <div className="space-y-3 text-xs">
            <div>
              <span className="text-slate-400 block font-medium">Objective:</span>
              <p className="text-slate-200 font-semibold mt-1 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
                {intent.objective}
              </p>
            </div>

            <div>
              <span className="text-slate-400 block font-medium">Sub-Tasks Identified:</span>
              <div className="flex gap-1.5 flex-wrap mt-1">
                {intent.tasks?.map((t, i) => (
                  <span key={i} className="px-2.5 py-1 rounded-md bg-blue-950 text-blue-300 border border-blue-800 font-mono">
                    {t}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <span className="text-slate-400 block font-medium">Target Columns:</span>
              <div className="flex gap-1.5 flex-wrap mt-1">
                {intent.required_columns?.map((c, i) => (
                  <span key={i} className="px-2.5 py-1 rounded-md bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
                    {c}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Analysis Execution Plan */}
      <div className="glass-card rounded-2xl p-6 space-y-4 border border-slate-800">
        <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm border-b border-slate-800 pb-3">
          <ListOrdered className="w-4 h-4" />
          <span>LangGraph Execution Plan</span>
        </div>

        <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
          {plan?.map((step, idx) => (
            <div key={idx} className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-2.5 text-xs">
              <span className="w-5 h-5 rounded-full bg-blue-950 border border-blue-700 text-blue-300 flex items-center justify-center font-bold shrink-0 text-[10px]">
                {step.step || idx + 1}
              </span>
              <div>
                <span className="font-semibold text-slate-200 capitalize">{step.action?.replace(/_/g, ' ')}</span>
                <p className="text-slate-400 text-[11px] mt-0.5">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AnalysisPlan;
