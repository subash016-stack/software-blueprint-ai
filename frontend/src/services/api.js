/**
 * Centralized API Service for Software Blueprint AI backend endpoints.
 */
import axios from 'axios';

const api = axios.create({
  baseURL: '',
  timeout: 600000, // 10 mins for local multi-agent LLM pipeline generations
  headers: {
    'Content-Type': 'application/json',
  },
});

export const createProject = async (projectIdea, projectName = null) => {
  const response = await api.post('/projects', {
    project_idea: projectIdea,
    project_name: projectName,
  }, {
    timeout: 600000, // 10 minutes
  });
  return response.data;
};

export const getProjects = async () => {
  const response = await api.get('/projects');
  return response.data;
};

export const getProjectBlueprint = async (projectId) => {
  const response = await api.get(`/projects/${projectId}/blueprint`);
  return response.data;
};

export const getArchitecture = async (projectId) => {
  const response = await api.get(`/projects/${projectId}/architecture`);
  return response.data;
};

export const getTraceability = async (projectId, highlight = null) => {
  const url = highlight ? `/projects/${projectId}/traceability?highlight=${highlight}` : `/projects/${projectId}/traceability`;
  const response = await api.get(url);
  return response.data;
};

export const getValidation = async (projectId) => {
  const response = await api.get(`/projects/${projectId}/validation`);
  return response.data;
};

export const getSources = async (projectId) => {
  const response = await api.get(`/projects/${projectId}/sources`);
  return response.data;
};

export const getVersions = async (projectId) => {
  const response = await api.get(`/projects/${projectId}/versions`);
  return response.data;
};

export const analyzeImpact = async (projectId, requirementId, payload) => {
  const response = await api.post(`/projects/${projectId}/requirements/${requirementId}/impact`, payload);
  return response.data;
};

export const refineBlueprint = async (projectId, payload) => {
  const response = await api.post(`/projects/${projectId}/refine`, payload, {
    timeout: 600000,
  });
  return response.data;
};

export const getMetrics = async () => {
  const response = await api.get('/metrics');
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getRagDocuments = async () => {
  const response = await api.get('/rag/documents');
  return response.data;
};

export const getRagChunks = async () => {
  const response = await api.get('/rag/chunks');
  return response.data;
};

export const getQdrantInfo = async () => {
  const response = await api.get('/rag/qdrant-info');
  return response.data;
};

export const reindexRag = async () => {
  const response = await api.post('/rag/reindex');
  return response.data;
};

export default api;
