import React from 'react';
import { CheckCircle2, AlertTriangle, RefreshCw, Loader2, Sparkles } from 'lucide-react';

export const AgentProgress = ({ loading, status, result, error }) => {
  if (!loading && !result && !error) return null;

  const retryCount = result?.retry_count || 0;
  const isFailed = result?.status === 'execution_failed' || (result?.execution_result && !result.execution_result.success && retryCount >= 3);
  const isCompleted = result?.status === 'completed' || (result?.report && result?.execution_result?.success);

  // Workflow steps status definition based on result state
  const steps = [
    { label: 'Dataset loaded', done: true },
    { label: 'Dataset profiled', done: true },
    { label: 'Intent understood', done: Boolean(result?.intent) || loading },
    { label: 'Analysis plan created', done: Boolean(result?.analysis_plan) || loading },
    { label: 'Code generated', done: Boolean(result?.generated_code) || loading },
    { label: 'Code validated', done: Boolean(result?.validated_code) || (retryCount > 0) },
    { label: 'Code executed', done: Boolean(result?.execution_result?.success) },
    { label: 'Visualizations generated', done: Boolean(result?.charts && result.charts.length > 0) },
    { label: 'Insights generated', done: Boolean(result?.insights && result.insights.length > 0) },
    { label: 'Report generated', done: Boolean(result?.report) },
  ];

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-blue-400" />
          <h4 className="font-bold text-white text-sm">Agent Workflow Status</h4>
        </div>

        <div>
          {loading ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-950 border border-blue-600 text-blue-300 text-xs font-mono">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Orchestrating Graph...</span>
            </span>
          ) : isCompleted ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950 border border-emerald-600 text-emerald-300 text-xs font-mono">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Execution Completed</span>
            </span>
          ) : isFailed ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-950 border border-rose-600 text-rose-300 text-xs font-mono">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
              <span>Execution Halted</span>
            </span>
          ) : null}
        </div>
      </div>

      {/* Error & Repair Retry Banner */}
      {retryCount > 0 && (
        <div className="p-3.5 rounded-xl border border-amber-500/40 bg-amber-950/20 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-amber-300">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>⚠ Analysis failed. Repairing generated code...</span>
            </div>
            <span className="px-2.5 py-0.5 rounded-full bg-amber-900/80 border border-amber-600 text-amber-200 font-mono text-[11px]">
              Retry {retryCount}/3
            </span>
          </div>
          <div className="flex items-center gap-2 text-emerald-300 pt-1.5 border-t border-amber-800/40">
            <RefreshCw className="w-3.5 h-3.5 text-emerald-400" />
            <span>Code repaired successfully. Continuing analysis automatically...</span>
          </div>
        </div>
      )}

      {/* Step Checklist */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5 pt-1">
        {steps.map((step, idx) => (
          <div
            key={idx}
            className={`p-2.5 rounded-xl border flex items-center gap-2 text-xs transition-all ${
              step.done
                ? 'bg-emerald-950/30 border-emerald-800/60 text-emerald-300'
                : loading
                ? 'bg-slate-900/50 border-slate-800 text-slate-400'
                : 'bg-slate-950/20 border-slate-900 text-slate-500'
            }`}
          >
            {step.done ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : loading ? (
              <div className="w-3.5 h-3.5 rounded-full border-2 border-slate-500 border-t-transparent animate-spin shrink-0" />
            ) : (
              <div className="w-3.5 h-3.5 rounded-full border border-slate-700 shrink-0" />
            )}
            <span className="truncate font-medium">{step.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgentProgress;
