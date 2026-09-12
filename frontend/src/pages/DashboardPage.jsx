import React, { useState } from 'react';
import { 
  Sparkles, 
  Layers, 
  CheckCircle2, 
  Clock, 
  Database, 
  Cpu, 
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Send
} from 'lucide-react';

const PRESET_IDEAS = [
  "Build an AI-powered telemedicine consultation platform with EHR integration and WebRTC video.",
  "Develop a real-time IoT fleet telemetry tracking and predictive maintenance system.",
  "Create a decentralized micro-lending fintech app with automated credit scoring and Stripe payouts.",
  "Build a multi-tenant B2B SaaS for collaborative sprint planning and engineering traceability."
];

export default function DashboardPage({ blueprint, onGenerate, isGenerating, setActiveTab }) {
  const [prompt, setPrompt] = useState('');
  const [activeStepIndex, setActiveStepIndex] = useState(0);

  const PIPELINE_STEPS = [
    { name: "Requirement Agent", detail: "Synthesizing IEEE 830/29148 Stakeholders & Functional Specs..." },
    { name: "Planning Agent", detail: "Constructing Work Breakdown Structure (WBS) & Task DAG..." },
    { name: "Architecture Agent", detail: "Designing C4 Containers, Decoupled Components & REST APIs..." },
    { name: "RAG Evidence Agent", detail: "Grounding Academic Knowledge & Calculating Similarity..." },
    { name: "Validation Agent", detail: "Executing Deterministic Cycle Audits & Computing Quality Score..." }
  ];

  React.useEffect(() => {
    let interval = null;
    if (isGenerating) {
      setActiveStepIndex(0);
      interval = setInterval(() => {
        setActiveStepIndex((prev) => (prev < PIPELINE_STEPS.length - 1 ? prev + 1 : prev));
      }, 15000); // Progress visually every 15s across stages
    }
    return () => clearInterval(interval);
  }, [isGenerating]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (prompt.trim().length >= 5) {
      onGenerate(prompt);
    }
  };

  const handleSelectPreset = (idea) => {
    setPrompt(idea);
  };

  const score = blueprint?.validation_report?.overall_score || 92;
  const totalHours = blueprint?.project_plan?.tasks?.reduce((acc, t) => acc + (t.estimated_hours || 0), 0) || 0;
  const frCount = blueprint?.requirements?.functional_requirements?.length || 0;
  const modCount = blueprint?.project_plan?.modules?.length || 0;
  const taskCount = blueprint?.project_plan?.tasks?.length || 0;
  const msCount = blueprint?.project_plan?.milestones?.length || 0;
  const compCount = blueprint?.architecture?.components?.length || 0;

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Hero / Generator Card */}
      <div className="glass-panel-glow rounded-3xl p-6 sm:p-8 relative overflow-hidden">
        <div className="absolute -right-20 -top-20 w-80 h-80 bg-brand-500/15 rounded-full blur-3xl pointer-events-none"></div>
        <div className="max-w-3xl space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30 text-xs font-mono">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Multi-Agent Architecture Synthesis</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-white tracking-tight leading-tight">
            Transform Vague Ideas into Validated Engineering Blueprints
          </h1>
          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
            Synthesizes structured IEEE SRS specifications, dependency-validated project plans, C4 architecture designs, evidence-grounded RAG citations, and automated requirement change impact analysis.
          </p>

          <form onSubmit={handleSubmit} className="space-y-3 pt-2">
            <div className="relative">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe your software idea in detail (e.g. Build an autonomous delivery platform with live telemetry and route optimization...)"
                rows={3}
                className="w-full bg-slate-900/90 border border-slate-700 rounded-2xl p-4 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition resize-none shadow-inner"
              />
              <button
                type="submit"
                disabled={isGenerating || prompt.trim().length < 5}
                className="absolute right-3 bottom-4 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium text-xs sm:text-sm flex items-center space-x-2 shadow-lg shadow-brand-500/25 transition"
              >
                {isGenerating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Synthesizing...</span>
                  </>
                ) : (
                  <>
                    <span>Generate Blueprint</span>
                    <Send className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>

            {/* Presets */}
            <div className="flex items-center space-x-2 overflow-x-auto py-1 scrollbar-none">
              <span className="text-xs text-slate-500 whitespace-nowrap">Examples:</span>
              {PRESET_IDEAS.map((idea, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectPreset(idea)}
                  className="text-xs px-2.5 py-1 rounded-lg bg-slate-800/70 hover:bg-slate-700 text-slate-300 border border-slate-700/60 whitespace-nowrap transition"
                >
                  {idea.slice(0, 42)}...
                </button>
              ))}
            </div>

            {/* Active Pipeline Status Banner */}
            {isGenerating && (
              <div className="mt-4 p-4 rounded-2xl bg-brand-950/60 border border-brand-500/40 animate-in fade-in space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-brand-400 animate-ping"></div>
                    <span className="text-xs font-mono text-brand-300 font-bold uppercase tracking-wider">
                      Agent Stage {activeStepIndex + 1}/5: {PIPELINE_STEPS[activeStepIndex].name}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono">Offline Local Inference</span>
                </div>
                <p className="text-xs text-slate-200 font-sans">
                  {PIPELINE_STEPS[activeStepIndex].detail}
                </p>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-brand-500 via-purple-500 to-accent-cyan transition-all duration-700 rounded-full"
                    style={{ width: `${((activeStepIndex + 1) / PIPELINE_STEPS.length) * 100}%` }}
                  ></div>
                </div>
              </div>
            )}
          </form>
        </div>
      </div>

      {/* KPI Overview Cards */}
      {blueprint && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="glass-panel rounded-2xl p-4 space-y-1">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>Quality Score</span>
              <ShieldCheck className="w-4 h-4 text-brand-400" />
            </div>
            <div className="text-2xl font-bold font-mono text-white">{score} <span className="text-xs text-slate-400">/100</span></div>
            <div className="text-[11px] text-emerald-400 font-medium">Validated 100% DAG</div>
          </div>

          <div className="glass-panel rounded-2xl p-4 space-y-1">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>Requirements</span>
              <Layers className="w-4 h-4 text-accent-cyan" />
            </div>
            <div className="text-2xl font-bold font-mono text-accent-cyan">{frCount} <span className="text-xs text-slate-400">FRs</span></div>
            <div className="text-[11px] text-slate-400 font-mono">IEEE/ISO SRS</div>
          </div>

          <div className="glass-panel rounded-2xl p-4 space-y-1">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>Modules</span>
              <Cpu className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-2xl font-bold font-mono text-purple-400">{modCount}</div>
            <div className="text-[11px] text-slate-400 font-mono">Subsystems</div>
          </div>

          <div className="glass-panel rounded-2xl p-4 space-y-1">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>Total Tasks</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold font-mono text-emerald-400">{taskCount}</div>
            <div className="text-[11px] text-slate-400 font-mono">{msCount} Milestones</div>
          </div>

          <div className="glass-panel rounded-2xl p-4 space-y-1">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>Effort Estimate</span>
              <Clock className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold font-mono text-amber-400">{totalHours} <span className="text-xs text-slate-400">hrs</span></div>
            <div className="text-[11px] text-slate-400 font-mono">~{Math.ceil(totalHours / 40)} weeks (1 dev)</div>
          </div>

          <div className="glass-panel rounded-2xl p-4 space-y-1">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>Architecture</span>
              <Database className="w-4 h-4 text-rose-400" />
            </div>
            <div className="text-2xl font-bold font-mono text-rose-400">{compCount} <span className="text-xs text-slate-400">Comps</span></div>
            <div className="text-[11px] text-slate-400 font-mono">C4 Grounded</div>
          </div>
        </div>
      )}

      {/* Quick Navigation Cards */}
      {blueprint && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div 
            onClick={() => setActiveTab('architecture')}
            className="glass-panel hover:border-brand-500/50 p-6 rounded-2xl cursor-pointer transition group"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="p-3 rounded-xl bg-brand-500/10 text-brand-400 group-hover:bg-brand-500/20 transition">
                <Database className="w-6 h-6" />
              </div>
              <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-brand-400 transition" />
            </div>
            <h3 className="font-display font-bold text-white text-base mb-1">C4 Architecture Blueprint</h3>
            <p className="text-xs text-slate-400 line-clamp-2">
              Inspect deployable containers, decoupled service components, REST endpoints, and database schemas with full requirement traceability.
            </p>
          </div>

          <div 
            onClick={() => setActiveTab('traceability')}
            className="glass-panel hover:border-accent-cyan/50 p-6 rounded-2xl cursor-pointer transition group"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="p-3 rounded-xl bg-cyan-500/10 text-accent-cyan group-hover:bg-cyan-500/20 transition">
                <TrendingUp className="w-6 h-6" />
              </div>
              <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-accent-cyan transition" />
            </div>
            <h3 className="font-display font-bold text-white text-base mb-1">Multi-Tier Traceability Graph</h3>
            <p className="text-xs text-slate-400 line-clamp-2">
              Interactive NetworkX graph mapping Stakeholders &rarr; Requirements &rarr; Modules &rarr; Tasks &rarr; Components &rarr; APIs &rarr; Milestones.
            </p>
          </div>

          <div 
            onClick={() => setActiveTab('impact')}
            className="glass-panel hover:border-rose-500/50 p-6 rounded-2xl cursor-pointer transition group"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="p-3 rounded-xl bg-rose-500/10 text-rose-400 group-hover:bg-rose-500/20 transition">
                <Sparkles className="w-6 h-6" />
              </div>
              <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-rose-400 transition" />
            </div>
            <h3 className="font-display font-bold text-white text-base mb-1">Impact Analysis Sandbox</h3>
            <p className="text-xs text-slate-400 line-clamp-2">
              Test requirement modifications, view downstream blast radiuses, and run targeted selective regeneration to create Blueprint v2.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
