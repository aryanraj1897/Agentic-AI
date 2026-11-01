import React, { useState } from 'react';
import { BarChart3, Maximize2, Download, Image as ImageIcon } from 'lucide-react';

export const Charts = ({ charts }) => {
  const [selectedChart, setSelectedChart] = useState(null);

  if (!charts || charts.length === 0) return null;

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-indigo-400" />
          <h4 className="font-bold text-white text-sm">Generated Visualizations ({charts.length})</h4>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {charts.map((chart, idx) => {
          const imgUrl = chart.url || `/api/analysis/charts/${chart.filename}`;
          return (
            <div
              key={idx}
              className="glass-card rounded-xl p-4 border border-slate-800 space-y-3 hover:border-slate-700 transition-all group"
            >
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-0.5 rounded-full bg-indigo-950 border border-indigo-700 text-indigo-300 font-mono text-[11px] uppercase">
                  {chart.type?.replace(/_/g, ' ') || 'Chart'}
                </span>
                <button
                  type="button"
                  onClick={() => setSelectedChart(imgUrl)}
                  className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 transition-colors"
                  title="Expand Chart"
                >
                  <Maximize2 className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Chart Image Container */}
              <div
                onClick={() => setSelectedChart(imgUrl)}
                className="bg-[#050810] border border-slate-800 rounded-xl overflow-hidden cursor-pointer flex items-center justify-center p-2 min-h-[200px]"
              >
                <img
                  src={imgUrl}
                  alt={chart.filename || `Chart ${idx + 1}`}
                  className="max-h-64 object-contain group-hover:scale-[1.02] transition-transform duration-200"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = 'https://via.placeholder.com/600x400/0f172a/38bdf8?text=Generated+Chart+Visualization';
                  }}
                />
              </div>

              <p className="text-xs text-slate-400">{chart.description || `Generated ${chart.type} visualization.`}</p>
            </div>
          );
        })}
      </div>

      {/* Expanded Chart Preview Modal */}
      {selectedChart && (
        <div
          onClick={() => setSelectedChart(null)}
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="glass-panel max-w-4xl w-full rounded-2xl p-6 border border-slate-700 space-y-4"
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <ImageIcon className="w-4 h-4 text-indigo-400" />
                Full Chart Preview
              </h3>
              <button
                onClick={() => setSelectedChart(null)}
                className="px-3 py-1 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs"
              >
                Close (ESC)
              </button>
            </div>

            <div className="bg-[#050810] rounded-xl p-4 flex items-center justify-center">
              <img src={selectedChart} alt="Full Chart" className="max-h-[70vh] object-contain" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Charts;
