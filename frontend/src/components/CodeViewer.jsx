import React, { useState } from 'react';
import { Code2, ChevronDown, ChevronUp, Copy, Check, Terminal } from 'lucide-react';

export const CodeViewer = ({ code, stdout, stderr }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!code) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-panel rounded-2xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Code2 className="w-5 h-5 text-indigo-400" />
          <h4 className="font-bold text-white text-sm">Generated Python Code (Optional View)</h4>
        </div>

        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs text-blue-300 font-semibold flex items-center gap-2 transition-colors cursor-pointer"
        >
          <span>{isOpen ? 'Hide Generated Code' : 'View Generated Code'}</span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {isOpen && (
        <div className="space-y-4 pt-2 border-t border-slate-800/80">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono">Python 3.13 (Pandas, Seaborn, Matplotlib)</span>
            <button
              type="button"
              onClick={handleCopy}
              className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center gap-1.5 border border-slate-700"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied!' : 'Copy Code'}</span>
            </button>
          </div>

          <div className="bg-[#050810] border border-slate-800 rounded-xl p-4 font-mono text-xs text-indigo-300 overflow-x-auto">
            <pre>{code}</pre>
          </div>

          {stdout && (
            <div className="space-y-1">
              <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
                <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                Raw Console Stdout Output:
              </span>
              <div className="bg-[#050810] border border-slate-800 rounded-xl p-3 font-mono text-[11px] text-emerald-400 overflow-x-auto">
                <pre>{stdout}</pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CodeViewer;
