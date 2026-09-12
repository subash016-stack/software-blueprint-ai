import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MetricsModal from './components/MetricsModal';
import DashboardPage from './pages/DashboardPage';
import RequirementsPage from './pages/RequirementsPage';
import ProjectPlanPage from './pages/ProjectPlanPage';
import ArchitecturePage from './pages/ArchitecturePage';
import TraceabilityPage from './pages/TraceabilityPage';
import RAGEvidencePage from './pages/RAGEvidencePage';
import ValidationPage from './pages/ValidationPage';
import ImpactAnalysisPage from './pages/ImpactAnalysisPage';
import VersionsPage from './pages/VersionsPage';
import { createProject, getProjectBlueprint, getProjects } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [blueprint, setBlueprint] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isMetricsOpen, setIsMetricsOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const [selectedReqForImpact, setSelectedReqForImpact] = useState('');

  // Initial load: try to fetch latest project if available
  useEffect(() => {
    const initFetch = async () => {
      try {
        const projects = await getProjects();
        if (projects && projects.length > 0) {
          const latest = await getProjectBlueprint(projects[projects.length - 1].id);
          setBlueprint(latest);
        }
      } catch (e) {
        console.log('No existing projects found or backend starting up.');
      }
    };
    initFetch();
  }, []);

  const handleGenerate = async (idea) => {
    setIsGenerating(true);
    setErrorMessage('');
    try {
      const data = await createProject(idea);
      setBlueprint(data);
      setActiveTab('dashboard');
    } catch (err) {
      console.error('Generation error:', err);
      const detail = err.response?.data?.detail || err.message || 'Generation failed. Verify Ollama is running.';
      setErrorMessage(detail);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleBlueprintUpdated = (updatedBp) => {
    setBlueprint(updatedBp);
  };

  const handleSimulateImpact = (reqId) => {
    setSelectedReqForImpact(reqId);
    setActiveTab('impact');
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans selection:bg-brand-500 selection:text-white">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        blueprint={blueprint}
        onOpenMetrics={() => setIsMetricsOpen(true)}
        isGenerating={isGenerating}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {errorMessage && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs sm:text-sm font-medium flex items-center justify-between animate-in fade-in">
            <span>{errorMessage}</span>
            <button
              onClick={() => setErrorMessage('')}
              className="text-rose-400 hover:text-white font-bold ml-4"
            >
              &times;
            </button>
          </div>
        )}

        {activeTab === 'dashboard' && (
          <DashboardPage
            blueprint={blueprint}
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
            setActiveTab={setActiveTab}
          />
        )}
        {activeTab === 'requirements' && (
          <RequirementsPage
            blueprint={blueprint}
            onSimulateImpact={handleSimulateImpact}
          />
        )}
        {activeTab === 'plan' && <ProjectPlanPage blueprint={blueprint} />}
        {activeTab === 'architecture' && <ArchitecturePage blueprint={blueprint} />}
        {activeTab === 'traceability' && <TraceabilityPage blueprint={blueprint} />}
        {activeTab === 'rag' && <RAGEvidencePage blueprint={blueprint} />}
        {activeTab === 'validation' && <ValidationPage blueprint={blueprint} />}
        {activeTab === 'impact' && (
          <ImpactAnalysisPage
            blueprint={blueprint}
            onBlueprintUpdated={handleBlueprintUpdated}
            initialRequirementId={selectedReqForImpact}
          />
        )}
        {activeTab === 'versions' && <VersionsPage blueprint={blueprint} />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/40 py-6 text-center text-xs text-slate-500 font-mono">
        <div>Software Blueprint AI • Full Multi-Agent Pipeline (Modules 1–6)</div>
        <div className="text-[11px] text-slate-600 mt-1">100% Offline Local Inference • Ollama Qwen • Qdrant RAG • Redis Cache</div>
      </footer>

      {/* Metrics Modal */}
      <MetricsModal
        isOpen={isMetricsOpen}
        onClose={() => setIsMetricsOpen(false)}
      />
    </div>
  );
}
