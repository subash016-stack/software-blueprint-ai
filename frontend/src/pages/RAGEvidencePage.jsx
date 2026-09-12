import React from 'react';
import { BookOpen, ShieldCheck, Cpu, ExternalLink, CheckCircle, AlertCircle } from 'lucide-react';

export default function RAGEvidencePage({ blueprint }) {
  const recommendations = blueprint?.rag_recommendations || [];

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center text-slate-400">
        <BookOpen className="w-12 h-12 mx-auto mb-3 text-slate-600" />
        <p>No RAG evidence loaded. Generate a blueprint to see grounded recommendations.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex items-center space-x-2 text-brand-400 text-xs font-mono mb-1">
          <BookOpen className="w-4 h-4" />
          <span>Module 4 — Academic Retrieval-Augmented Generation (RAG) Grounding</span>
        </div>
        <h2 className="text-2xl font-display font-bold text-white mb-2">Evidence-Grounded Architectural Rationale</h2>
        <p className="text-sm text-slate-300 leading-relaxed max-w-4xl">
          Every architectural recommendation below is strictly retrieved and grounded against peer-reviewed software engineering literature and authoritative design patterns stored in Qdrant. No fabricated citations.
        </p>
      </div>

      {/* Recommendations Cards */}
      <div className="space-y-6">
        {recommendations.map((rec, idx) => (
          <div key={idx} className="glass-panel rounded-2xl p-6 space-y-4 border-l-4 border-l-brand-500">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center space-x-2">
                <span className="font-mono text-xs font-bold text-brand-400 px-2.5 py-0.5 rounded bg-brand-500/10 border border-brand-500/20">
                  TOPIC {idx + 1}
                </span>
                <h3 className="font-display font-bold text-white text-base">{rec.topic}</h3>
              </div>
              <div className="flex items-center space-x-2 text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded-full self-start sm:self-auto">
                <CheckCircle className="w-3.5 h-3.5" />
                <span>Confidence: {Math.round(rec.confidence * 100)}%</span>
              </div>
            </div>

            {/* Recommendation Statement */}
            <div className="text-sm text-slate-200 font-medium leading-relaxed bg-slate-900/60 p-4 rounded-xl border border-slate-800">
              {rec.recommendation}
            </div>

            {/* Tradeoffs */}
            {rec.tradeoffs && (
              <div className="text-xs text-slate-300 space-y-1">
                <span className="font-semibold text-amber-400 font-mono">Architectural Trade-offs: </span>
                <span>{rec.tradeoffs}</span>
              </div>
            )}

            {/* Evidence Citations */}
            {rec.evidence && rec.evidence.length > 0 && (
              <div className="space-y-2 pt-2 border-t border-slate-800">
                <div className="text-xs font-bold text-slate-400 font-mono">Retrieved Knowledge Citations:</div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {rec.evidence.map((ev, evIdx) => (
                    <div key={evIdx} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-[11px] text-accent-cyan font-semibold">{ev.source_id}</span>
                        <span className="text-[10px] font-mono text-slate-500">Score: {ev.relevance_score}</span>
                      </div>
                      <div className="text-xs font-bold text-white">{ev.title}</div>
                      <div className="text-[11px] text-brand-300 font-mono">{ev.section}</div>
                      <p className="text-[11px] text-slate-400 leading-relaxed italic bg-black/30 p-2 rounded border border-slate-800/80">
                        "{ev.excerpt}"
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
