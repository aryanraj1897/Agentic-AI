import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { uploadDataset, getDatasetProfile } from '../services/api';

export const DatasetUpload = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (!file) return;

    const allowedExtensions = ['.csv', '.xlsx', '.xls', '.json'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowedExtensions.includes(fileExt)) {
      setError(`Unsupported file format "${fileExt}". Please upload a CSV, XLSX, or JSON file.`);
      setSelectedFile(null);
      return;
    }

    setError(null);
    setSelectedFile(file);
    processUpload(file);
  };

  const processUpload = async (file) => {
    setUploading(true);
    setError(null);

    const uploadRes = await uploadDataset(file);

    if (!uploadRes.success) {
      setError(uploadRes.error);
      setUploading(false);
      return;
    }

    const metadata = uploadRes.data;

    // Fetch full profile immediately
    const profileRes = await getDatasetProfile(metadata.dataset_id);

    setUploading(false);

    if (profileRes.success) {
      if (onUploadSuccess) {
        onUploadSuccess(metadata, profileRes.data);
      }
    } else {
      setError(`Uploaded successfully, but failed to load profile: ${profileRes.error}`);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <UploadCloud className="w-5 h-5 text-blue-400" />
            Dataset Upload & Automatic Profiler
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Upload your dataset to generate instant statistical profiling and structural analysis.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
            CSV
          </span>
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
            XLSX
          </span>
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
            JSON
          </span>
        </div>
      </div>

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
          isDragging
            ? 'border-blue-500 bg-blue-950/40 shadow-lg shadow-blue-500/10 scale-[0.99]'
            : 'border-slate-700/80 hover:border-blue-500/60 hover:bg-slate-900/40 bg-slate-950/20'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv, .xlsx, .xls, .json"
          onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
          className="hidden"
        />

        <div className="flex flex-col items-center gap-3">
          {uploading ? (
            <div className="p-3 rounded-full bg-blue-950/60 border border-blue-500/30 text-blue-400">
              <Loader2 className="w-8 h-8 animate-spin" />
            </div>
          ) : (
            <div className="p-3 rounded-full bg-slate-800/80 border border-slate-700 text-slate-300">
              <UploadCloud className="w-8 h-8 text-blue-400" />
            </div>
          )}

          <div>
            <p className="text-sm font-semibold text-slate-200">
              {uploading
                ? 'Processing & Profiling Dataset...'
                : selectedFile
                ? selectedFile.name
                : 'Drag & Drop your dataset here, or click to browse'}
            </p>
            <p className="text-xs text-slate-400 mt-1">
              Supports CSV, Excel (.xlsx), and JSON datasets (Up to 50MB)
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

export default DatasetUpload;
