import React, { useEffect, useState } from 'react';
import { checkHealth, uploadDataset, getDatasetProfile, startAnalysis, getAnalysesHistory, getAnalysisById } from '../services/api';
import HealthBadge from '../components/HealthBadge';
import DatasetUpload from '../components/DatasetUpload';
import DatasetPreview from '../components/DatasetPreview';
import ChatInterface from '../components/ChatInterface';
import AnalysisPlan from '../components/AnalysisPlan';
import AgentProgress from '../components/AgentProgress';
import Results from '../components/Results';
import AnalysisHistory from '../components/AnalysisHistory';
import { Database, AlertTriangle, FileSpreadsheet, Sparkles } from 'lucide-react';

export const Dashboard = () => {
  const [healthState, setHealthState] = useState({
    isConnected: false,
    loading: true,
    data: null,
    error: null,
  });

  // State management for uploaded datasets and active analysis
  const [datasetsList, setDatasetsList] = useState([]);
  const [activeDataset, setActiveDataset] = useState(null);
  const [activeProfile, setActiveProfile] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);

  // Live execution state
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  const fetchHealth = async () => {
    setHealthState((prev) => ({ ...prev, loading: true }));
    const result = await checkHealth();
    setHealthState({
      isConnected: result.success,
      loading: false,
      data: result.success ? result.data : null,
      error: result.success ? null : result.error,
    });
  };

  const fetchHistory = async () => {
    try {
      const res = await getAnalysesHistory();
      if (res.success && Array.isArray(res.data)) {
        setAnalysisHistory(res.data);
      }
    } catch (e) {
      console.warn('Failed to load analysis history:', e);
    }
  };

  useEffect(() => {
    fetchHealth();
    fetchHistory();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // Handler when a dataset is uploaded successfully
  const handleUploadSuccess = (metadata, profile) => {
    setActiveDataset(metadata);
    setActiveProfile(profile);

    setDatasetsList((prev) => {
      const exists = prev.some((d) => d.dataset_id === metadata.dataset_id);
      if (exists) return prev;
      return [
        {
          dataset_id: metadata.dataset_id,
          filename: metadata.filename,
          rows: metadata.rows,
          columns: metadata.columns,
          profile,
        },
        ...prev,
      ];
    });

    setAnalysisResult(null);
    setAnalysisError(null);
  };

  // Handler for running agent analysis workflow
  const handleRunAnalysis = async (queryToRun) => {
    if (!activeDataset?.dataset_id || !queryToRun) return;

    setAnalysisLoading(true);
    setAnalysisError(null);
    setAnalysisResult(null);

    try {
      const res = await startAnalysis(activeDataset.dataset_id, queryToRun);
      if (res.success) {
        setAnalysisResult(res.data);
        fetchHistory(); // Refresh history list from SQLite database
      } else {
        setAnalysisError(res.error || 'Analysis execution failed');
      }
    } catch (err) {
      setAnalysisError(err.message || 'Failed to execute analysis graph');
    } finally {
      setAnalysisLoading(false);
    }
  };

  // Select dataset from history sidebar
  const handleSelectDataset = (datasetItem) => {
    setActiveDataset({
      dataset_id: datasetItem.dataset_id,
      filename: datasetItem.filename,
      rows: datasetItem.rows,
      columns: datasetItem.columns,
    });
    setActiveProfile(datasetItem.profile);
    setAnalysisResult(null);
    setAnalysisError(null);
  };

  const handleSelectHistory = async (histItem) => {
    const analysisId = histItem.analysis_id || histItem.id;
    if (!analysisId) return;

    setAnalysisLoading(true);
    try {
      const res = await getAnalysisById(analysisId);
      if (res.success) {
        setAnalysisResult(res.data);
      }
    } catch (e) {
      console.warn('Failed to load single analysis details:', e);
    } finally {
      setAnalysisLoading(false);
    }
  };

  // Preload sample sales.csv dataset
  const loadSampleSalesDataset = async () => {
    const sampleSalesCsv = `product,region,sales,units,date,department
Widget Alpha,North,15000,120,2024-01-01,Hardware
Widget Beta,South,23000,180,2024-01-02,Software
Widget Alpha,East,18000,140,2024-01-03,Hardware
Widget Gamma,North,31000,250,2024-01-04,Cloud Services
Widget Beta,North,29000,210,2024-01-05,Software
Widget Gamma,South,42000,310,2024-01-06,Cloud Services
Widget Alpha,West,12000,95,2024-01-07,Hardware
Widget Beta,East,35000,270,2024-01-08,Software`;

    const blob = new Blob([sampleSalesCsv], { type: 'text/csv' });
    const file = new File([blob], 'sales.csv', { type: 'text/csv' });

    const uploadRes = await uploadDataset(file);
    if (uploadRes.success) {
      const profileRes = await getDatasetProfile(uploadRes.data.dataset_id);
      if (profileRes.success) {
        handleUploadSuccess(uploadRes.data, profileRes.data);
      }
    }
  };

  return (
    <div className="min-h-[calc(100vh-73px)] bg-[#090d16] text-slate-100 flex flex-col font-sans">
      {/* Top Header Status Bar */}
      <div className="border-b border-slate-800 bg-[#070a12] py-3 px-4 sm:px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-blue-950 border border-blue-800 text-blue-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white">Autonomous Data Analysis Agent</h2>
            <p className="text-[11px] text-slate-400">LangGraph Self-Healing Agent Architecture • Phases 1–8 Active</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <HealthBadge
            isConnected={healthState.isConnected}
            loading={healthState.loading}
            onRetry={fetchHealth}
          />
          {!activeProfile && (
            <button
              onClick={loadSampleSalesDataset}
              className="px-3.5 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-500/20 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <FileSpreadsheet className="w-3.5 h-3.5" />
              <span>Load sample sales.csv</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Grid Dashboard Layout */}
      <div className="flex-1 max-w-[1700px] w-full mx-auto p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Sidebar: Datasets & Analysis History (3 Cols) */}
        <div className="lg:col-span-3">
          <AnalysisHistory
            datasets={datasetsList}
            selectedDatasetId={activeDataset?.dataset_id}
            onSelectDataset={handleSelectDataset}
            history={analysisHistory}
            onSelectHistory={handleSelectHistory}
            onNewDataset={() => {
              setActiveDataset(null);
              setActiveProfile(null);
              setAnalysisResult(null);
            }}
          />
        </div>

        {/* Right Main Area: Analysis Workspace (9 Cols) */}
        <div className="lg:col-span-9 space-y-6">
          
          {/* Backend Offline Warning Banner */}
          {!healthState.isConnected && (
            <div className="p-4 rounded-2xl border bg-rose-950/30 border-rose-500/20 text-rose-300 backdrop-blur-md flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
                <div>
                  <h4 className="font-semibold text-xs">FastAPI Backend Offline</h4>
                  <p className="text-[11px] opacity-80">
                    Ensure Uvicorn server is running on port 8000 to enable LangGraph workflow analysis.
                  </p>
                </div>
              </div>
              <button
                onClick={fetchHealth}
                className="px-3 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium border border-slate-700 cursor-pointer"
              >
                Retry
              </button>
            </div>
          )}

          {/* 1. Dataset Upload Section */}
          {!activeProfile && (
            <DatasetUpload onUploadSuccess={handleUploadSuccess} />
          )}

          {/* 2. Dataset Preview Section */}
          {activeProfile && (
            <DatasetPreview metadata={activeDataset} profile={activeProfile} />
          )}

          {/* 3. Query Chat Interface */}
          <ChatInterface
            onRunAnalysis={handleRunAnalysis}
            loading={analysisLoading}
            datasetId={activeDataset?.dataset_id}
          />

          {/* 4. Live Agent Progress Step Checklist */}
          <AgentProgress
            loading={analysisLoading}
            status={analysisResult?.status}
            result={analysisResult}
            error={analysisError}
          />

          {/* 5. Analysis Plan & Intent Breakdown */}
          {analysisResult && (
            <AnalysisPlan
              intent={analysisResult.intent}
              plan={analysisResult.analysis_plan}
            />
          )}

          {/* 6. Comprehensive Analysis Results (Charts, Insights, Report, Optional Code Viewer) */}
          {analysisResult && (
            <Results result={analysisResult} />
          )}

          {/* Empty Workspace Placeholder */}
          {!activeProfile && (
            <div className="glass-card rounded-2xl p-12 text-center space-y-4 border border-slate-800">
              <div className="w-14 h-14 rounded-2xl bg-blue-950/60 border border-blue-500/30 text-blue-400 flex items-center justify-center mx-auto">
                <Database className="w-7 h-7" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">No Dataset Loaded</h3>
                <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
                  Upload a CSV, Excel (.xlsx), or JSON file above or click "Load sample sales.csv" to start automated data profiling and agent analysis.
                </p>
              </div>
              <button
                onClick={loadSampleSalesDataset}
                className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-500/20 inline-flex items-center gap-2 cursor-pointer"
              >
                <FileSpreadsheet className="w-4 h-4" />
                <span>Load sample sales.csv</span>
              </button>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};

export default Dashboard;
