import React, { useState } from 'react';
import {
  FileSpreadsheet,
  Layers,
  Table as TableIcon,
  Search,
  CheckCircle2,
  AlertCircle,
  Hash,
  Type,
  Calendar,
  ToggleLeft,
  Key,
  Copy
} from 'lucide-react';

export const DatasetProfile = ({ profile }) => {
  const [searchTerm, setSearchTerm] = useState('');

  if (!profile) return null;

  const {
    filename,
    rows,
    columns,
    file_type,
    file_size_bytes,
    duplicate_rows,
    duplicate_percentage,
    total_missing_values,
    total_missing_percentage,
    numeric_columns = [],
    categorical_columns = [],
    date_columns = [],
    boolean_columns = [],
    constant_columns = [],
    potential_id_columns = [],
    column_profiles = {},
  } = profile;

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const filteredColumns = Object.keys(column_profiles).filter((colName) =>
    colName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <div className="glass-card rounded-2xl p-6 relative overflow-hidden border border-slate-800">
        <div className="flex items-center justify-between flex-wrap gap-4 border-b border-slate-800/80 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-blue-950/80 border border-blue-500/30 text-blue-400">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight">{filename}</h2>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                ID: {profile.dataset_id} • Uploaded {new Date(profile.created_at).toLocaleString()}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <span className="px-3 py-1 rounded-full bg-blue-950 text-blue-300 border border-blue-800 text-xs font-semibold">
              {file_type} ({formatBytes(file_size_bytes)})
            </span>
            <span className="px-3 py-1 rounded-full bg-slate-800 text-slate-200 border border-slate-700 text-xs font-semibold">
              {rows.toLocaleString()} Rows
            </span>
            <span className="px-3 py-1 rounded-full bg-slate-800 text-slate-200 border border-slate-700 text-xs font-semibold">
              {columns.toLocaleString()} Columns
            </span>
          </div>
        </div>

        {/* Data Quality & Column Classification Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 mt-4">
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
            <div className="flex items-center justify-center gap-1.5 text-blue-400 text-xs font-medium mb-1">
              <Hash className="w-3.5 h-3.5" />
              <span>Numeric</span>
            </div>
            <span className="text-lg font-bold text-white">{numeric_columns.length}</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
            <div className="flex items-center justify-center gap-1.5 text-emerald-400 text-xs font-medium mb-1">
              <Type className="w-3.5 h-3.5" />
              <span>Categorical</span>
            </div>
            <span className="text-lg font-bold text-white">{categorical_columns.length}</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
            <div className="flex items-center justify-center gap-1.5 text-purple-400 text-xs font-medium mb-1">
              <Calendar className="w-3.5 h-3.5" />
              <span>Date</span>
            </div>
            <span className="text-lg font-bold text-white">{date_columns.length}</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
            <div className="flex items-center justify-center gap-1.5 text-amber-400 text-xs font-medium mb-1">
              <ToggleLeft className="w-3.5 h-3.5" />
              <span>Boolean</span>
            </div>
            <span className="text-lg font-bold text-white">{boolean_columns.length}</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
            <div className="flex items-center justify-center gap-1.5 text-indigo-400 text-xs font-medium mb-1">
              <Key className="w-3.5 h-3.5" />
              <span>Potential ID</span>
            </div>
            <span className="text-lg font-bold text-white">{potential_id_columns.length}</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
            <div className="flex items-center justify-center gap-1.5 text-rose-400 text-xs font-medium mb-1">
              <Copy className="w-3.5 h-3.5" />
              <span>Duplicates</span>
            </div>
            <span className="text-lg font-bold text-white">{duplicate_rows} ({duplicate_percentage}%)</span>
          </div>
        </div>

        {/* Missing Values Notice */}
        <div className="mt-4 p-3 rounded-xl bg-slate-900/40 border border-slate-800 flex items-center justify-between text-xs text-slate-300">
          <div className="flex items-center gap-2">
            {total_missing_values > 0 ? (
              <AlertCircle className="w-4 h-4 text-amber-400" />
            ) : (
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            )}
            <span>
              Total Missing Values: <strong className="text-white">{total_missing_values.toLocaleString()}</strong> ({total_missing_percentage}% of total dataset cells)
            </span>
          </div>

          {duplicate_rows > 0 && (
            <span className="text-amber-400 font-medium">
              ⚠️ {duplicate_rows} duplicate rows detected
            </span>
          )}
        </div>
      </div>

      {/* Detailed Columns Table */}
      <div className="glass-panel rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2">
            <TableIcon className="w-5 h-5 text-blue-400" />
            <h3 className="font-bold text-white">Dataset Profile Statistics</h3>
          </div>

          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search column..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-1.5 bg-slate-900 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 w-56"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider bg-slate-900/50">
                <th className="py-3 px-4">Column Name</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Missing</th>
                <th className="py-3 px-4">Unique</th>
                <th className="py-3 px-4">Mean</th>
                <th className="py-3 px-4">Median</th>
                <th className="py-3 px-4">Std Dev</th>
                <th className="py-3 px-4">Min / Max</th>
                <th className="py-3 px-4">Sample Values</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {filteredColumns.map((colName) => {
                const col = column_profiles[colName];
                return (
                  <tr key={colName} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-semibold text-white font-sans flex items-center gap-2">
                      {col.is_numeric && <span className="w-2 h-2 rounded-full bg-blue-500" title="Numeric" />}
                      {col.is_categorical && <span className="w-2 h-2 rounded-full bg-emerald-500" title="Categorical" />}
                      {col.is_date && <span className="w-2 h-2 rounded-full bg-purple-500" title="Date" />}
                      {col.is_boolean && <span className="w-2 h-2 rounded-full bg-amber-500" title="Boolean" />}
                      {col.is_potential_id && <span className="w-2 h-2 rounded-full bg-indigo-500" title="ID" />}
                      <span>{colName}</span>
                    </td>

                    <td className="py-3 px-4 text-slate-300">
                      <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-[10px]">
                        {col.dtype}
                      </span>
                    </td>

                    <td className="py-3 px-4">
                      {col.missing_count > 0 ? (
                        <span className="text-amber-400">
                          {col.missing_count} ({col.missing_percentage}%)
                        </span>
                      ) : (
                        <span className="text-slate-500">0 (0%)</span>
                      )}
                    </td>

                    <td className="py-3 px-4 text-slate-300">
                      {col.unique_count.toLocaleString()}
                    </td>

                    <td className="py-3 px-4 text-slate-300">
                      {col.mean !== null ? col.mean.toFixed(2) : '-'}
                    </td>

                    <td className="py-3 px-4 text-slate-300">
                      {col.median !== null ? col.median.toFixed(2) : '-'}
                    </td>

                    <td className="py-3 px-4 text-slate-300">
                      {col.std !== null ? col.std.toFixed(2) : '-'}
                    </td>

                    <td className="py-3 px-4 text-slate-300">
                      {col.min !== null && col.max !== null ? (
                        <span>{String(col.min)} / {String(col.max)}</span>
                      ) : (
                        '-'
                      )}
                    </td>

                    <td className="py-3 px-4 text-slate-400 font-sans max-w-xs truncate">
                      {col.sample_values && col.sample_values.length > 0
                        ? col.sample_values.join(', ')
                        : '-'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DatasetProfile;
