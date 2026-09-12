import React, { useState } from 'react';
import { 
  Sparkles, 
  Layers, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowRight, 
  Cpu, 
  Database, 
  Clock, 
  RefreshCw,
  Zap,
  TrendingUp
} from 'lucide-react';
import { analyzeImpact, refineBlueprint } from '../services/api';

export default function ImpactAnalysisPage({ blueprint, onBlueprintUpdated, initialRequirementId }) {
  const [selectedFrId, setSelectedFrId] = useState(initialRequirementId || '');
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [impactReport, setImpactReport] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const { functional_requirements } = blueprint?.requirements || {};

  const handleSelectFR = (frId) => {
    setSelectedFrId(frId);
    const fr = functional_requirements?.find((r) => r.id === frId);
    if (fr) {
      setNewTitle(fr.title);
      setNewDescription(fr.description);
    }
    setImpactReport(null);
    setSuccessMessage('');
  };

  React.useEffect(() => {
    if (initialRequirementId && functional_requirements) {
      handleSelectFR(initialRequirementId);
    }
  }, [initialRequirementId, blueprint]);

  if (!blueprint?.requirements) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center text-slate-400">
        <Sparkles className="w-12 h-12 mx-auto mb-3 text-slate-600" />
        <p>No blueprint loaded. Generate a blueprint first to run Impact Analysis.</p>
      </div>
    );
  }

  const handleAnalyzeImpact = async (e) => {
    e.preventDefault();
    if (!selectedFrId || !newDescription) return;

    setIsAnalyzing(true);
    setSuccessMessage('');
    try {
      const report = await analyzeImpact(blueprint.project_id, selectedFrId, {
        requirement_id: selectedFrId,
        new_title: newTitle,
        new_description: newDescription,
      });
      setImpactReport(report);
    } catch (err) {
      console.error('Impact analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleApplyRegeneration = async () => {
    if (!impactReport) return;
    setIsRegenerating(true);
    try {
      const updatedBlueprint = await refineBlueprint(blueprint.project_id, {
        requirement_id: selectedFrId,
        new_title: newTitle,
        new_description: newDescription,
      });
      setSuccessMessage(`✅ Successfully generated Blueprint v${updatedBlueprint.version} via Targeted Selective Regeneration!`);
      if (onBlueprintUpdated) {
        onBlueprintUpdated(updatedBlueprint);
      }
    } catch (err) {
      console.error('Refine error:', err);
    } finally {
      setIsRegenerating(false);
    }
  };

  const getImpactBadge = (level) => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-300 border-orange-500/30';
      case 'MEDIUM':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      default:
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex items-center space-x-2 text-rose-400 text-xs font-mono mb-1">
          <Sparkles className="w-4 h-4" />
          <span>Module 6 — Requirement Change Impact Analysis & Targeted Selective Regeneration</span>
        </div>
        <h2 className="text-2xl font-display font-bold text-white mb-2">Requirement Change Impact Sandbox</h2>
        <p className="text-sm text-slate-300 leading-relaxed max-w-4xl">
          When software requirements evolve, modifying one entity should not force a blind rewrite of the entire system.
          This sandbox executes a deterministic NetworkX graph traversal to isolate the downstream blast radius and selectively regenerates only the affected tasks, components, and APIs.
        </p>
      </div>

      {successMessage && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm font-medium flex items-center space-x-2 animate-in fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Interactive Change Configuration Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Step 1: Select Requirement */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <Layers className="w-5 h-5 text-brand-400" />
            <h3>1. Select Target Requirement</h3>
          </div>

          <div className="glass-panel rounded-2xl p-4 space-y-2 max-h-[420px] overflow-y-auto">
            {(functional_requirements || []).map((fr) => {
              const isSelected = selectedFrId === fr.id;
              return (
                <button
                  key={fr.id}
                  onClick={() => handleSelectFR(fr.id)}
                  className={`w-full text-left p-3 rounded-xl transition flex flex-col space-y-1 ${
                    isSelected
                      ? 'bg-brand-600/30 border border-brand-500 text-white'
                      : 'bg-slate-900/60 border border-slate-800 text-slate-300 hover:bg-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-brand-400">{fr.id}</span>
                    <span className="text-[10px] font-mono text-slate-400">{fr.priority}</span>
                  </div>
                  <div className="text-xs font-medium text-white">{fr.title}</div>
                  <div className="text-[11px] text-slate-400 line-clamp-1">{fr.description}</div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Step 2: Propose Modification */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <Zap className="w-5 h-5 text-amber-400" />
            <h3>2. Propose Requirement Modification</h3>
          </div>

          <form onSubmit={handleAnalyzeImpact} className="glass-panel rounded-2xl p-6 space-y-4">
            {!selectedFrId ? (
              <div className="text-center py-10 text-slate-500 text-xs">
                &larr; Select a functional requirement on the left to propose an update.
              </div>
            ) : (
              <>
                <div className="space-y-1">
                  <label className="text-xs font-mono text-slate-400">Requirement Title</label>
                  <input
                    type="text"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-brand-500"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-mono text-slate-400">Updated Requirement Specification</label>
                  <textarea
                    rows={4}
                    value={newDescription}
                    onChange={(e) => setNewDescription(e.target.value)}
                    placeholder="Enter revised requirement specification..."
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-brand-500 resize-none"
                  />
                </div>

                <div className="flex items-center justify-between pt-2">
                  <div className="text-[11px] text-slate-400 font-mono">
                    Target: <span className="text-brand-400 font-bold">{selectedFrId}</span>
                  </div>
                  <button
                    type="submit"
                    disabled={isAnalyzing}
                    className="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white font-medium text-xs flex items-center space-x-2 shadow-lg shadow-rose-500/20 transition"
                  >
                    {isAnalyzing ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>Traversing Graph...</span>
                      </>
                    ) : (
                      <>
                        <TrendingUp className="w-4 h-4" />
                        <span>Analyze Downstream Impact</span>
                      </>
                    )}
                  </button>
                </div>
              </>
            )}
          </form>
        </div>
      </div>

      {/* Step 3: Blast Radius Analysis Report */}
      {impactReport && (
        <div className="glass-panel-glow rounded-3xl p-6 sm:p-8 space-y-6 animate-in fade-in zoom-in-95">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
            <div>
              <div className="text-xs text-rose-400 font-mono font-semibold">Downstream Blast Radius Analysis</div>
              <h3 className="text-xl font-display font-bold text-white">Impact on {impactReport.changed_requirement_id}</h3>
            </div>
            <div className="flex items-center space-x-3">
              <span className={`text-xs px-3 py-1 rounded-full border font-mono font-bold ${getImpactBadge(impactReport.impact_level)}`}>
                Impact Level: {impactReport.impact_level}
              </span>
              <div className="text-xs font-mono text-amber-400 bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20">
                Effort Delta: +{impactReport.effort_hours_delta} hrs
              </div>
            </div>
          </div>

          {/* Technical Explanation */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
            <div className="text-xs font-bold text-slate-400 font-mono">Architectural Blast Explanation:</div>
            <p className="text-xs text-slate-200 leading-relaxed">{impactReport.explanation}</p>
          </div>

          {/* Affected Entities Matrix */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
              <div className="text-[11px] text-purple-400 font-mono">Affected Modules</div>
              <div className="text-base font-bold font-mono text-white">{impactReport.affected_modules?.length || 0}</div>
              <div className="text-[10px] text-slate-400 font-mono">{(impactReport.affected_modules || []).join(', ') || 'None'}</div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
              <div className="text-[11px] text-emerald-400 font-mono">Affected Tasks</div>
              <div className="text-base font-bold font-mono text-white">{impactReport.affected_tasks?.length || 0}</div>
              <div className="text-[10px] text-slate-400 font-mono">{(impactReport.affected_tasks || []).join(', ') || 'None'}</div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
              <div className="text-[11px] text-rose-400 font-mono">Affected Components</div>
              <div className="text-base font-bold font-mono text-white">{impactReport.affected_components?.length || 0}</div>
              <div className="text-[10px] text-slate-400 font-mono">{(impactReport.affected_components || []).join(', ') || 'None'}</div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
              <div className="text-[11px] text-cyan-400 font-mono">Affected APIs</div>
              <div className="text-base font-bold font-mono text-white">{impactReport.affected_apis?.length || 0}</div>
              <div className="text-[10px] text-slate-400 font-mono">{(impactReport.affected_apis || []).join(', ') || 'None'}</div>
            </div>
          </div>

          {/* Action Trigger */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-4 border-t border-slate-800">
            <div className="text-xs text-slate-400 max-w-xl">
              Targeted Selective Regeneration will update <span className="text-white font-mono">{impactReport.changed_requirement_id}</span> and refine ONLY the {impactReport.affected_tasks?.length || 0} affected tasks and {impactReport.affected_components?.length || 0} affected components, preserving all other blueprint entities untouched.
            </div>
            <button
              onClick={handleApplyRegeneration}
              disabled={isRegenerating}
              className="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs flex items-center space-x-2 shadow-lg shadow-emerald-500/25 transition shrink-0"
            >
              {isRegenerating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Generating v{blueprint.version + 1}...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Apply &amp; Regenerate Blueprint v{blueprint.version + 1}</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
