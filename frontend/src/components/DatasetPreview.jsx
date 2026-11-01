import React from 'react';
import { Database, FileSpreadsheet, AlertTriangle, Layers, Table } from 'lucide-react';

export const DatasetPreview = ({ metadata, profile }) => {
  if (!profile && !metadata) return null;

  const datasetName = profile?.filename || metadata?.filename || 'Uploaded Dataset';
  const rowCount = profile?.rows ?? metadata?.rows ?? 0;
  const colCount = profile?.columns ?? metadata?.columns ?? 0;
  const missingValues = profile?.missing_values || {};
  const duplicateRows = profile?.duplicate_rows ?? 0;
  const sampleData = profile?.sample_data || [];
  const columnProfiles = profile?.column_profiles || {};

  const totalMissing = Object.values(missingValues).reduce((a, b) => a + b, 0);

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-6">
      {/* Overview Stat Cards */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-blue-950/80 border border-blue-500/30 text-blue-400">
            <FileSpreadsheet className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              {datasetName}
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
                ✓ Dataset Profiled
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Dataset ID: <span className="font-mono text-slate-300">{metadata?.dataset_id || profile?.dataset_id}</span>
            </p>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-xs">
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl px-4 py-2">
            <span className="text-slate-400 block text-[10px]">TOTAL ROWS</span>
            <span className="text-sm font-bold text-white font-mono">{rowCount.toLocaleString()}</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-xl px-4 py-2">
            <span className="text-slate-400 block text-[10px]">COLUMNS</span>
            <span className="text-sm font-bold text-blue-400 font-mono">{colCount}</span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-xl px-4 py-2">
            <span className="text-slate-400 block text-[10px]">MISSING VALUES</span>
            <span className={`text-sm font-bold font-mono ${totalMissing > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
              {totalMissing}
            </span>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 rounded-xl px-4 py-2">
            <span className="text-slate-400 block text-[10px]">DUPLICATES</span>
            <span className={`text-sm font-bold font-mono ${duplicateRows > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {duplicateRows}
            </span>
          </div>
        </div>
      </div>

      {/* Column Schema Pills */}
      <div>
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <Layers className="w-4 h-4 text-blue-400" />
          <span>Column Attributes ({Object.keys(columnProfiles).length || colCount})</span>
        </h4>

        <div className="flex gap-2 flex-wrap max-h-32 overflow-y-auto pr-1">
          {Object.entries(columnProfiles).map(([colName, info], idx) => (
            <div
              key={idx}
              className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2 text-xs"
            >
              <span className="font-mono text-slate-200 font-semibold">{colName}</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-blue-300 font-mono">
                {info.type || 'string'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Sample Data Table Preview */}
      {sampleData.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <Table className="w-4 h-4 text-emerald-400" />
            <span>Sample Data Preview (First 5 Rows)</span>
          </h4>

          <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-900 border-b border-slate-800 text-slate-400 font-mono">
                  {Object.keys(sampleData[0]).map((header, i) => (
                    <th key={i} className="px-4 py-2.5 font-semibold text-slate-300">
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-slate-300">
                {sampleData.slice(0, 5).map((row, rowIdx) => (
                  <tr key={rowIdx} className="hover:bg-slate-900/40 transition-colors">
                    {Object.values(row).map((val, cellIdx) => (
                      <td key={cellIdx} className="px-4 py-2 whitespace-nowrap">
                        {val !== null && val !== undefined ? String(val) : <span className="text-slate-600 italic">null</span>}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default DatasetPreview;
