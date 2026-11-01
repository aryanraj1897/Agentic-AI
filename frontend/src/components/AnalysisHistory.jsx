import React from 'react';
import { Database, Clock, ChevronRight, FileSpreadsheet, Plus, Calendar } from 'lucide-react';

export const AnalysisHistory = ({
  datasets,
  selectedDatasetId,
  onSelectDataset,
  history,
  onSelectHistory,
  onNewDataset
}) => {

  const formatDate = (dateStr) => {
    if (!dateStr) return '29 Sep 2026';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return '29 Sep 2026';
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch {
      return '29 Sep 2026';
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-5 space-y-6 h-full border border-slate-800">
      {/* Sidebar Header & New Dataset Button */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-400" />
            Datasets & History
          </h3>
        </div>

        <button
          type="button"
          onClick={onNewDataset}
          className="w-full py-2.5 px-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20 transition-all cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Upload New Dataset</span>
        </button>
      </div>

      {/* Datasets List */}
      <div className="space-y-2">
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
          Uploaded Datasets ({datasets.length})
        </span>

        {datasets.length === 0 ? (
          <div className="p-3 rounded-xl bg-slate-900/40 border border-slate-800 text-center text-xs text-slate-500 italic">
            No datasets uploaded yet.
          </div>
        ) : (
          <div className="space-y-1.5 max-h-44 overflow-y-auto pr-1">
            {datasets.map((item) => {
              const isSelected = item.dataset_id === selectedDatasetId;
              return (
                <div
                  key={item.dataset_id}
                  onClick={() => onSelectDataset(item)}
                  className={`p-3 rounded-xl border text-xs cursor-pointer transition-all flex items-center justify-between ${
                    isSelected
                      ? 'bg-blue-950/70 border-blue-600 text-white font-medium shadow-md shadow-blue-500/10'
                      : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:bg-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <FileSpreadsheet className={`w-4 h-4 shrink-0 ${isSelected ? 'text-blue-400' : 'text-slate-400'}`} />
                    <div className="truncate">
                      <p className="truncate font-semibold text-[11px]">{item.filename}</p>
                      <p className="text-[10px] text-slate-400">{item.rows} rows · {item.columns} cols</p>
                    </div>
                  </div>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Previous Analyses List (Phase 9 Format) */}
      <div className="space-y-2 pt-2 border-t border-slate-800">
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block flex items-center gap-1">
          <Clock className="w-3 h-3 text-emerald-400" />
          Previous Analyses ({history.length})
        </span>

        {history.length === 0 ? (
          <div className="p-3 rounded-xl bg-slate-900/40 border border-slate-800 text-center text-xs text-slate-500 italic">
            No previous analyses saved yet.
          </div>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {history.map((histItem, idx) => (
              <div
                key={histItem.id || histItem.analysis_id || idx}
                onClick={() => onSelectHistory(histItem)}
                className="p-3 rounded-xl bg-slate-900/70 hover:bg-slate-800/90 border border-slate-800 hover:border-slate-700 text-xs cursor-pointer transition-all space-y-1 group"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-200 text-[11px] group-hover:text-blue-300 transition-colors truncate max-w-[140px]">
                    {histItem.filename ? `${histItem.filename.replace(/\.[^/.]+$/, '')} Analysis` : 'Data Analysis'}
                  </span>
                  <span className="text-[10px] text-slate-400 flex items-center gap-1 font-mono">
                    <Calendar className="w-3 h-3 text-slate-500" />
                    {formatDate(histItem.created_at || histItem.completed_at)}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-2 leading-snug">
                  "{histItem.user_query}"
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisHistory;
