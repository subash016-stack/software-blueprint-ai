import React from 'react';
import { ShieldCheck, AlertCircle, AlertTriangle, CheckCircle2, TrendingUp, Cpu } from 'lucide-react';

export default function ValidationPage({ blueprint }) {
  if (!blueprint?.validation_report) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center text-slate-400">
        <ShieldCheck className="w-12 h-12 mx-auto mb-3 text-slate-600" />
        <p>No validation audit loaded. Please generate or load a blueprint first.</p>
      </div>
    );
  }

  const { overall_score, score_breakdown, critical_issues, warnings, recommendations, is_valid } = blueprint.validation_report;

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-brand-400 text-xs font-mono mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Module 5 — Deterministic Audit & Multi-Dimensional Quality Scoring</span>
          </div>
          <h2 className="text-2xl font-display font-bold text-white">Blueprint Quality & Audit Report</h2>
        </div>
        <div className="flex items-center space-x-4 bg-slate-900/80 p-4 rounded-2xl border border-slate-800">
          <div>
            <div className="text-[11px] text-slate-400">Quality Score</div>
            <div className="text-3xl font-bold font-mono text-emerald-400">{overall_score} <span className="text-xs text-slate-400">/ 100</span></div>
          </div>
          <div className="w-px h-10 bg-slate-700"></div>
          <div>
            <div className="text-[11px] text-slate-400">Audit Status</div>
            <div className={`text-sm font-bold font-mono ${is_valid ? 'text-emerald-400' : 'text-rose-400'}`}>
              {is_valid ? 'PASSED (0 Critical)' : 'ACTION NEEDED'}
            </div>
          </div>
        </div>
      </div>

      {/* 6-Dimension Score Breakdown */}
      {score_breakdown && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="glass-panel rounded-2xl p-4 space-y-1 text-center">
            <div className="text-[11px] text-slate-400">Requirements</div>
            <div className="text-xl font-bold font-mono text-accent-cyan">{score_breakdown.requirement_quality}%</div>
            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div className="bg-accent-cyan h-full" style={{ width: `${score_breakdown.requirement_quality}%` }}></div>
            </div>
          </div>

          <div className="glass-panel rounded-2xl p-4 space-y-1 text-center">
            <div className="text-[11px] text-slate-400">Traceability</div>
            <div className="text-xl font-bold font-mono text-brand-400">{score_breakdown.traceability_coverage}%</div>
            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div className="bg-brand-500 h-full" style={{ width: `${score_breakdown.traceability_coverage}%` }}></div>
            </div>
          </div>

          <div className="glass-panel rounded-2xl p-4 space-y-1 text-center">
            <div className="text-[11px] text-slate-400">Architecture</div>
            <div className="text-xl font-bold font-mono text-purple-400">{score_breakdown.architecture_consistency}%</div>
            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div className="bg-purple-500 h-full" style={{ width: `${score_breakdown.architecture_consistency}%` }}></div>
            </div>
          </div>

          <div className="glass-panel rounded-2xl p-4 space-y-1 text-center">
            <div className="text-[11px] text-slate-400">DAG Validity</div>
            <div className="text-xl font-bold font-mono text-emerald-400">{score_breakdown.dependency_validity}%</div>
            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div className="bg-emerald-500 h-full" style={{ width: `${score_breakdown.dependency_validity}%` }}></div>
            </div>
          </div>

          <div className="glass-panel rounded-2xl p-4 space-y-1 text-center">
            <div className="text-[11px] text-slate-400">NFR Coverage</div>
            <div className="text-xl font-bold font-mono text-amber-400">{score_breakdown.nfr_coverage}%</div>
            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div className="bg-amber-500 h-full" style={{ width: `${score_breakdown.nfr_coverage}%` }}></div>
            </div>
          </div>

          <div className="glass-panel rounded-2xl p-4 space-y-1 text-center">
            <div className="text-[11px] text-slate-400">RAG Grounding</div>
            <div className="text-xl font-bold font-mono text-rose-400">{score_breakdown.rag_grounding_score}%</div>
            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div className="bg-rose-500 h-full" style={{ width: `${score_breakdown.rag_grounding_score}%` }}></div>
            </div>
          </div>
        </div>
      )}

      {/* Critical Issues & Warnings */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Critical Issues */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <AlertCircle className="w-5 h-5 text-rose-400" />
            <h3>Critical Structural Issues</h3>
            <span className="text-xs font-mono text-slate-400">({critical_issues?.length || 0})</span>
          </div>

          {critical_issues && critical_issues.length > 0 ? (
            <div className="space-y-3">
              {critical_issues.map((iss, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-rose-400 font-mono">{iss.code}</span>
                    {iss.entity_id && (
                      <span className="text-[11px] font-mono bg-rose-950 text-rose-200 px-2 py-0.5 rounded">
                        {iss.entity_id}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-200">{iss.message}</p>
                  {iss.recommendation && (
                    <div className="text-[11px] text-rose-300 font-mono pt-1">Fix: {iss.recommendation}</div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-panel rounded-xl p-6 text-center text-slate-400 space-y-2">
              <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-400" />
              <p className="text-xs font-medium text-slate-200">Zero Critical Issues Detected</p>
              <p className="text-[11px] text-slate-500">All task DAGs, IDs, and traceability links are verified valid.</p>
            </div>
          )}
        </div>

        {/* Warnings & Recommendations */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <h3>Audit Recommendations</h3>
            <span className="text-xs font-mono text-slate-400">({recommendations?.length || 0})</span>
          </div>

          <div className="glass-panel rounded-2xl p-5 space-y-3">
            {(recommendations || []).map((rec, idx) => (
              <div key={idx} className="flex items-start space-x-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="w-5 h-5 rounded-full bg-brand-500/20 text-brand-300 flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  {idx + 1}
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
