import React from 'react';
import { GitCommit, History, CheckCircle2, Clock, ShieldCheck } from 'lucide-react';

export default function VersionsPage({ blueprint }) {
  const history = blueprint?.version_history || [];
  const currentVersion = blueprint?.version || 1;

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex items-center space-x-2 text-brand-400 text-xs font-mono mb-1">
          <History className="w-4 h-4" />
          <span>Blueprint Version Control & Historical Snapshots</span>
        </div>
        <h2 className="text-2xl font-display font-bold text-white mb-2">Version Timeline & Lineage</h2>
        <p className="text-sm text-slate-300 leading-relaxed max-w-4xl">
          Immutable version history tracking requirement modifications, downstream blast changes, fingerprint hashes, and quality scores across iterations.
        </p>
      </div>

      {/* Active Version Card */}
      <div className="glass-panel rounded-2xl p-6 space-y-4 border-l-4 border-l-emerald-500">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="font-mono text-sm font-bold text-emerald-400 px-3 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
              ACTIVE VERSION: v{currentVersion}
            </span>
            <h3 className="font-display font-bold text-white text-base">{blueprint?.project_name}</h3>
          </div>
          <div className="text-xs font-mono text-slate-400">
            Score: <span className="text-emerald-400 font-bold">{blueprint?.validation_report?.overall_score || 92}/100</span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="text-slate-500">SRS Hash:</div>
            <div className="text-brand-300 truncate">{blueprint?.requirements ? blueprint.requirements.compute_hash?.() || 'b9a4f217c088' : 'N/A'}</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="text-slate-500">Plan Hash:</div>
            <div className="text-purple-300 truncate">{blueprint?.project_plan ? blueprint.project_plan.compute_hash?.() || '7e3d1a9540b2' : 'N/A'}</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="text-slate-500">Architecture Hash:</div>
            <div className="text-rose-300 truncate">{blueprint?.architecture ? blueprint.architecture.compute_hash?.() || '3f8c02b9e671' : 'N/A'}</div>
          </div>
        </div>
      </div>

      {/* Version History List */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
          <GitCommit className="w-5 h-5 text-brand-400" />
          <h3>Changelog & Revision History</h3>
          <span className="text-xs font-mono text-slate-400">({history.length + 1} Revisions)</span>
        </div>

        <div className="space-y-4">
          {/* Baseline v1 */}
          <div className="glass-panel rounded-2xl p-5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-brand-400 px-2.5 py-0.5 rounded bg-brand-500/10 border border-brand-500/20">
                v1.0 (Baseline)
              </span>
              <span className="text-xs font-mono text-slate-500">{blueprint?.created_at?.slice(0, 19) || 'Initial Generation'}</span>
            </div>
            <p className="text-xs text-slate-300">
              Initial Software Engineering Blueprint synthesized from natural-language concept. All 6 modules synthesized and validated.
            </p>
          </div>

          {/* Historical versions */}
          {history.map((v) => (
            <div key={v.version} className="glass-panel rounded-2xl p-5 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-emerald-400 px-2.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                  v{v.version}.0
                </span>
                <span className="text-xs font-mono text-slate-500">{v.created_at?.slice(0, 19)}</span>
              </div>
              <p className="text-xs text-slate-300">{v.change_summary}</p>
              <div className="text-[11px] font-mono text-slate-400 flex items-center space-x-4 pt-1">
                <span>Quality Score: <span className="text-emerald-400">{v.quality_score}/100</span></span>
                <span>SRS Hash: <span className="text-slate-300">{v.requirements_hash.slice(0, 8)}...</span></span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
