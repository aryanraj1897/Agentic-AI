const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message || 'Failed to connect to backend' };
  }
};

export const uploadDataset = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE_URL}/api/datasets/upload`, {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || `Upload failed with status ${response.status}`);
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message || 'Failed to upload dataset' };
  }
};

export const getDatasetMetadata = async (datasetId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/datasets/${datasetId}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to fetch dataset metadata');
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const getDatasetProfile = async (datasetId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/datasets/${datasetId}/profile`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to fetch dataset profile');
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const startAnalysis = async (datasetId, userQuery, analysisId = null) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analysis/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dataset_id: datasetId,
        user_query: userQuery,
        ...(analysisId ? { analysis_id: analysisId } : {}),
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to start analysis workflow');
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const getAnalysisResults = async (analysisId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analyses/${analysisId}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to fetch analysis results');
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const getAnalysisCharts = async (analysisId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analysis/${analysisId}/charts`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to fetch analysis charts');
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const getAnalysesHistory = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analyses`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to fetch analyses history');
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

export const getAnalysisById = async (analysisId) => {
  return getAnalysisResults(analysisId);
};

export const deleteAnalysisById = async (analysisId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analyses/${analysisId}`, {
      method: 'DELETE',
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to delete analysis');
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
};
