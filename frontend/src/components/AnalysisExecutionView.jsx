import React, { useState } from 'react';
import { Play, Sparkles, Terminal, Code2, CheckCircle2, ListOrdered, FileCode, Copy, Check, ShieldCheck, AlertTriangle, RefreshCw, Image as ImageIcon } from 'lucide-react';
import { startAnalysis } from '../services/api';

export const AnalysisExecutionView = ({ datasetId, datasetProfile }) => {
  const [userQuery, setUserQuery] = useState('Find the top 10 products by revenue and show monthly trends.');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const sampleQueries = [
    'Find the top 10 products by revenue.',
    'Show monthly sales trends.',
    'Analyze regional performance.',
  ];

  const handleRunAnalysis = async (queryToRun) => {
    const query = queryToRun || userQuery;
    if (!query.trim() || !datasetId) return;

    setLoading(true);
    setError(null);

    try {
      const res = await startAnalysis(datasetId, query);
      if (res.success) {
        setResult(res.data);
      } else {
        setError(res.error);
      }
    } catch (err) {
      setError(err.message || 'Failed to execute analysis graph');
    } finally {
      setLoading(false);
    }
  };

  const copyCode = () => {
    if (result?.generated_code) {
      navigator.clipboard.writeText(result.generated_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Query Input Section */}
      <div className="glass-panel rounded-2xl p-6 space-y-4">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-400" />
            Autonomous AI Analysis Agent (Phase 5 Sandboxed Execution)
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Ask questions about your dataset. LangGraph orchestrates intent analysis, execution planning, AST security validation, and sandboxed Python code execution.
          </p>
        </div>

        <div className="flex gap-2 flex-wrap">
          {sampleQueries.map((q, idx) => (
            <button
              key={idx}
              onClick={() => {
                setUserQuery(q);
                handleRunAnalysis(q);
              }}
              className="text-xs px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-blue-300 border border-slate-700 transition-colors"
            >
              "{q}"
            </button>
          ))}
        </div>

        <div className="flex gap-3">
          <input
            type="text"
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)}
            placeholder="Type your data query (e.g. Find top products by revenue)..."
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-sans"
          />
          <button
            onClick={() => handleRunAnalysis(userQuery)}
            disabled={loading || !datasetId}
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2 shrink-0 disabled:opacity-50"
          >
            {loading ? (
              <span>Executing Sandbox Graph...</span>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                <span>Run Agent Graph</span>
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs">
            {error}
          </div>
        )}
      </div>

      {/* Analysis Results */}
      {result && (
        <div className="space-y-6">
          {/* Intent & Plan Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Intent Analysis */}
            <div className="glass-card rounded-2xl p-6 space-y-3 border border-slate-800">
              <div className="flex items-center gap-2 text-blue-400 font-bold text-sm border-b border-slate-800 pb-3">
                <Sparkles className="w-4 h-4" />
                <span>1. Intent Analysis & Classification</span>
              </div>

              {result.intent && (
                <div className="space-y-3 text-xs">
                  <div>
                    <span className="text-slate-400 block font-medium">Objective:</span>
                    <p className="text-slate-200 font-semibold mt-0.5">{result.intent.objective}</p>
                  </div>

                  <div>
                    <span className="text-slate-400 block font-medium">Tasks:</span>
                    <div className="flex gap-1.5 flex-wrap mt-1">
                      {result.intent.tasks?.map((t, i) => (
                        <span key={i} className="px-2.5 py-1 rounded-md bg-blue-950 text-blue-300 border border-blue-800/80 font-mono">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <span className="text-slate-400 block font-medium">Target Dataset Columns:</span>
                    <div className="flex gap-1.5 flex-wrap mt-1">
                      {result.intent.required_columns?.map((c, i) => (
                        <span key={i} className="px-2.5 py-1 rounded-md bg-emerald-950 text-emerald-300 border border-emerald-800/80 font-mono">
                          {c}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Analysis Plan */}
            <div className="glass-card rounded-2xl p-6 space-y-3 border border-slate-800">
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm border-b border-slate-800 pb-3">
                <ListOrdered className="w-4 h-4" />
                <span>2. Execution Plan</span>
              </div>

              <div className="space-y-2">
                {result.analysis_plan?.map((step, idx) => (
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

          {/* Self-Healing Repair Banner (Phase 6) */}
          {result.retry_count > 0 && (
            <div className="glass-card rounded-2xl p-4 border border-amber-500/40 bg-amber-950/20 space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 font-bold text-amber-300">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span>Analysis failed. Repairing generated code...</span>
                </div>
                <span className="px-2.5 py-0.5 rounded-full bg-amber-900/80 border border-amber-600 text-amber-200 font-mono text-[11px]">
                  Retry {result.retry_count}/3
                </span>
              </div>
              <div className="flex items-center gap-2 text-emerald-300 pt-1 border-t border-amber-800/40">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Code repaired successfully. Continue analysis.</span>
              </div>
            </div>
          )}

          {/* Validation & Sandbox Execution Results */}
          <div className="glass-panel rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <Terminal className="w-5 h-5 text-emerald-400" />
                <h4 className="font-bold text-white text-sm">3. Sandboxed Execution Output</h4>
              </div>

              <div className="flex items-center gap-2">
                {result.retry_count > 0 && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-950/80 border border-amber-500/40 text-amber-300 text-xs font-medium">
                    <RefreshCw className="w-3.5 h-3.5 text-amber-400 animate-spin-slow" />
                    <span>Repaired (Retry {result.retry_count}/3)</span>
                  </span>
                )}
                {result.validated_code ? (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-xs font-medium">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                    <span>AST Validated ✓</span>
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs font-medium">
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                    <span>Security Validation Failed</span>
                  </span>
                )}
              </div>
            </div>

            {/* Subprocess Stdout Output Terminal */}
            {result.execution_result && (
              <div className="bg-[#050810] border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-200 overflow-x-auto space-y-2">
                <div className="text-slate-500 text-[11px] border-b border-slate-800/80 pb-2 flex items-center justify-between">
                  <span>Sandbox Terminal Output</span>
                  <span>Execution Status: {result.execution_result.success ? 'Success (200)' : 'Failed'}</span>
                </div>

                {result.execution_result.stdout ? (
                  <pre className="text-emerald-400 whitespace-pre-wrap">{result.execution_result.stdout}</pre>
                ) : (
                  <p className="text-slate-500 italic">No console output generated.</p>
                )}

                {result.execution_result.stderr && (
                  <div className="pt-2 border-t border-slate-800">
                    <span className="text-rose-400 font-bold block mb-1">Errors / Warnings:</span>
                    <pre className="text-amber-400/90 whitespace-pre-wrap text-[11px]">
                      {result.execution_result.stderr}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Phase 7 Insights & Visualization Artifacts */}
          {result.insights && result.insights.length > 0 && (
            <div className="glass-panel rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
                <Sparkles className="w-5 h-5 text-amber-400" />
                <h4 className="font-bold text-white text-sm">5. Key Data Insights</h4>
              </div>

              <ul className="space-y-2 text-xs text-slate-300">
                {result.insights.map((insight, i) => (
                  <li key={i} className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                    <span className="w-2 h-2 rounded-full bg-amber-400 shrink-0 mt-1.5" />
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Phase 7 Executive Markdown Report */}
          {result.report && (
            <div className="glass-panel rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <FileCode className="w-5 h-5 text-blue-400" />
                  <h4 className="font-bold text-white text-sm">6. Generated Executive Markdown Report</h4>
                </div>
                <span className="text-[11px] font-mono px-2.5 py-1 rounded-lg bg-blue-950 text-blue-300 border border-blue-800">
                  {result.analysis_id || 'ID: Phase 7 Report'}
                </span>
              </div>

              <div className="bg-[#050810] border border-slate-800/80 rounded-xl p-5 font-mono text-xs text-slate-200 overflow-x-auto">
                <pre className="whitespace-pre-wrap leading-relaxed">{result.report}</pre>
              </div>
            </div>
          )}

          {/* Generated Code Section */}
          <div className="glass-panel rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Code2 className="w-5 h-5 text-indigo-400" />
                <h4 className="font-bold text-white text-sm">7. Python Analysis Code</h4>
              </div>

              <button
                onClick={copyCode}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center gap-1.5 border border-slate-700"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied!' : 'Copy Code'}</span>
              </button>
            </div>

            <div className="bg-[#050810] border border-slate-800/80 rounded-xl p-4 font-mono text-xs text-indigo-300 overflow-x-auto">
              <pre>{result.generated_code}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisExecutionView;
