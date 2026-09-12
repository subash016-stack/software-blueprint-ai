import React from 'react';
import { Cpu, Activity, Layers, Sparkles, Database, GitCommit } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, blueprint, onOpenMetrics, isGenerating }) {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'requirements', label: 'SRS Requirements', icon: Layers },
    { id: 'plan', label: 'Project Plan', icon: Sparkles },
    { id: 'architecture', label: 'Architecture C4', icon: Database },
    { id: 'traceability', label: 'Traceability Graph', icon: GitCommit },
    { id: 'rag', label: 'RAG Evidence', icon: Cpu },
    { id: 'validation', label: 'Validation & Score', icon: Activity },
    { id: 'impact', label: 'Impact Sandbox', icon: Sparkles },
    { id: 'versions', label: 'Versions', icon: GitCommit },
  ];

  return (
    <header className="border-b border-slate-800 bg-[#0f172a]/95 sticky top-0 z-40 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-accent-cyan flex items-center justify-center shadow-lg shadow-brand-500/20">
              <Cpu className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-display font-bold text-lg text-white tracking-tight">Software Blueprint AI</span>
                {blueprint && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-400 border border-brand-500/30 font-mono">
                    v{blueprint.version || 1}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 font-sans hidden sm:block">
                Multi-Agent Requirements Engineering & Traceability Platform
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {blueprint && (
              <div className="relative group">
                <button
                  className="flex items-center space-x-1.5 text-xs px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-medium shadow-sm transition"
                  title="Export Engineering Blueprint in Multiple Formats"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Export Dossier</span>
                </button>
                <div className="absolute right-0 mt-1 w-52 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl py-1 hidden group-hover:block z-50 animate-in fade-in">
                  <a
                    href={`/api/v1/projects/${blueprint.project_id}/export/markdown`}
                    download={`${blueprint.project_name.toLowerCase().replace(/\\s+/g, '_')}_srs_dossier.md`}
                    className="block px-3 py-2 text-xs text-slate-200 hover:bg-slate-800 hover:text-white transition"
                  >
                    📄 <strong>Markdown Dossier (.md)</strong>
                    <div className="text-[10px] text-slate-400">IEEE 830 SRS + Plan + C4</div>
                  </a>
                  <a
                    href={`/api/v1/projects/${blueprint.project_id}/export/openapi`}
                    download={`${blueprint.project_name.toLowerCase().replace(/\\s+/g, '_')}_openapi.json`}
                    className="block px-3 py-2 text-xs text-slate-200 hover:bg-slate-800 hover:text-white transition border-t border-slate-800"
                  >
                    ⚡ <strong>OpenAPI 3.0 Spec (.json)</strong>
                    <div className="text-[10px] text-slate-400">Swagger / Postman ready</div>
                  </a>
                  <a
                    href={`/api/v1/projects/${blueprint.project_id}/export/jira`}
                    download={`${blueprint.project_name.toLowerCase().replace(/\\s+/g, '_')}_jira_backlog.json`}
                    className="block px-3 py-2 text-xs text-slate-200 hover:bg-slate-800 hover:text-white transition border-t border-slate-800"
                  >
                    🎯 <strong>Jira / Backlog (.json)</strong>
                    <div className="text-[10px] text-slate-400">Epics, stories & tasks</div>
                  </a>
                  <a
                    href={`/api/v1/projects/${blueprint.project_id}/blueprint`}
                    download={`${blueprint.project_name.toLowerCase().replace(/\\s+/g, '_')}_blueprint_v${blueprint.version}.json`}
                    className="block px-3 py-2 text-xs text-slate-200 hover:bg-slate-800 hover:text-white transition border-t border-slate-800"
                  >
                    📦 <strong>Full Blueprint (.json)</strong>
                    <div className="text-[10px] text-slate-400">Complete raw schema</div>
                  </a>
                </div>
              </div>
            )}

            <button
              onClick={onOpenMetrics}
              className="flex items-center space-x-2 text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
              title="View Token & LLM Performance Metrics"
            >
              <Activity className="w-4 h-4 text-accent-cyan" />
              <span className="hidden md:inline font-mono">Metrics</span>
            </button>
            <div className="flex items-center space-x-2 text-xs px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Local Ollama • Qwen</span>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav className="flex space-x-1 overflow-x-auto py-2 scrollbar-none border-t border-slate-800/60">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-brand-600 text-white shadow-sm shadow-brand-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
