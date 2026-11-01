import React, { useState } from 'react';
import { BarChart3, Lightbulb, FileText, Code2, Layers } from 'lucide-react';
import { Charts } from './Charts';
import { Insights } from './Insights';
import { Report } from './Report';
import { CodeViewer } from './CodeViewer';

export const Results = ({ result }) => {
  const [activeTab, setActiveTab] = useState('all');

  if (!result) return null;

  const { charts = [], insights = [], report, generated_code, execution_result, analysis_id } = result;

  return (
    <div className="space-y-6">
      {/* View Filter Tabs Header */}
      <div className="glass-panel rounded-2xl p-3 flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setActiveTab('all')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer ${
              activeTab === 'all'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Full Overview</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('report')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer ${
              activeTab === 'report'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Executive Report</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('charts')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer ${
              activeTab === 'charts'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Visual Charts ({charts.length})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('insights')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer ${
              activeTab === 'insights'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            <Lightbulb className="w-3.5 h-3.5" />
            <span>Key Insights ({insights.length})</span>
          </button>
        </div>
      </div>

      {/* Tab Contents */}
      {(activeTab === 'all' || activeTab === 'insights') && (
        <Insights insights={insights} />
      )}

      {(activeTab === 'all' || activeTab === 'charts') && (
        <Charts charts={charts} />
      )}

      {(activeTab === 'all' || activeTab === 'report') && (
        <Report report={report} analysisId={analysis_id} />
      )}

      {/* Code Viewer (Optional) */}
      <CodeViewer
        code={generated_code}
        stdout={execution_result?.stdout}
        stderr={execution_result?.stderr}
      />
    </div>
  );
};

export default Results;
