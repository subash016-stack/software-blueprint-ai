import React, { useState } from 'react';
import { Database, Server, Cpu, Shield, Zap, Layers, Globe, Code, ArrowRight, CheckCircle } from 'lucide-react';

export default function ArchitecturePage({ blueprint }) {
  const [selectedComponent, setSelectedComponent] = useState(null);

  if (!blueprint?.architecture) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center text-slate-400">
        <Database className="w-12 h-12 mx-auto mb-3 text-slate-600" />
        <p>No architecture blueprint loaded. Please generate a blueprint first.</p>
      </div>
    );
  }

  const { architecture_style, overview, containers, components, apis, databases, adrs, security_strategy, scalability_strategy, deployment_topology } = blueprint.architecture;

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex items-center space-x-2 text-brand-400 text-xs font-mono mb-1">
          <Database className="w-4 h-4" />
          <span>Module 3 — Technical Architecture Blueprint (C4 Software Architecture Model)</span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
          <h2 className="text-2xl font-display font-bold text-white">System Architecture & Topology</h2>
          <span className="text-xs px-3 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30 font-mono font-semibold self-start">
            {architecture_style}
          </span>
        </div>
        <p className="text-sm text-slate-300 leading-relaxed max-w-4xl">{overview}</p>
      </div>

      {/* C4 Containers Tier */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
          <Server className="w-5 h-5 text-accent-cyan" />
          <h3>C4 Deployable Containers</h3>
          <span className="text-xs font-mono text-slate-400">({containers?.length || 0})</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(containers || []).map((cont) => (
            <div key={cont.id} className="glass-panel rounded-xl p-5 space-y-2 border-t-2 border-t-accent-cyan">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-accent-cyan px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
                  {cont.id}
                </span>
                <span className="text-xs font-mono text-slate-400">{cont.type}</span>
              </div>
              <h4 className="font-display font-bold text-white text-base">{cont.name}</h4>
              <div className="text-xs font-mono text-brand-300 bg-slate-900/80 px-2 py-1 rounded border border-slate-800">
                Tech: {cont.technology}
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{cont.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Architecture Components with Traceability Inspector */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
          <Cpu className="w-5 h-5 text-purple-400" />
          <h3>Architecture Components (Traceable to FRs)</h3>
          <span className="text-xs font-mono text-slate-400">({components?.length || 0})</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(components || []).map((comp) => {
            const isSelected = selectedComponent?.id === comp.id;
            return (
              <div
                key={comp.id}
                onClick={() => setSelectedComponent(isSelected ? null : comp)}
                className={`glass-panel rounded-xl p-5 space-y-3 cursor-pointer transition ${
                  isSelected ? 'border-brand-500 ring-1 ring-brand-500' : 'hover:border-slate-600'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-purple-400 px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20">
                    {comp.id}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">{comp.module_id || 'Core'}</span>
                </div>
                <h4 className="font-display font-bold text-white text-sm">{comp.name}</h4>
                <p className="text-xs text-slate-300 leading-relaxed">{comp.description}</p>

                <div className="pt-2 border-t border-slate-800 space-y-1 text-[11px]">
                  <div className="flex items-center space-x-1">
                    <span className="text-slate-500 font-mono">Traced FRs:</span>
                    {(comp.requirement_ids || []).map((r) => (
                      <span key={r} className="px-1.5 py-0.2 rounded bg-brand-500/20 text-brand-300 font-mono font-bold">
                        {r}
                      </span>
                    ))}
                  </div>
                  {comp.tech_stack && comp.tech_stack.length > 0 && (
                    <div className="flex flex-wrap gap-1 pt-1">
                      {comp.tech_stack.map((ts, idx) => (
                        <span key={idx} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono text-[10px]">
                          {ts}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* APIs & Databases */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Core APIs */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <Globe className="w-5 h-5 text-accent-cyan" />
            <h3>Defined API Endpoints</h3>
            <span className="text-xs font-mono text-slate-400">({apis?.length || 0})</span>
          </div>

          <div className="space-y-3">
            {(apis || []).map((api) => (
              <div key={api.id} className="glass-panel rounded-xl p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 rounded text-[11px] font-mono font-bold ${
                      api.method === 'GET' ? 'bg-emerald-500/20 text-emerald-300' :
                      api.method === 'POST' ? 'bg-brand-500/20 text-brand-300' :
                      api.method === 'PUT' ? 'bg-amber-500/20 text-amber-300' : 'bg-rose-500/20 text-rose-300'
                    }`}>
                      {api.method}
                    </span>
                    <span className="font-mono text-xs text-white font-semibold">{api.endpoint}</span>
                  </div>
                  <span className="font-mono text-[10px] text-slate-500">{api.id}</span>
                </div>
                <p className="text-xs text-slate-300">{api.summary}</p>
                <div className="flex items-center space-x-2 text-[11px] text-slate-400 pt-1">
                  <span>Owner: <span className="font-mono text-slate-300">{api.component_id}</span></span>
                  <span>•</span>
                  <span>FRs: <span className="font-mono text-brand-300">{(api.requirement_ids || []).join(', ')}</span></span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Databases */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <Database className="w-5 h-5 text-emerald-400" />
            <h3>Database & Persistence Models</h3>
            <span className="text-xs font-mono text-slate-400">({databases?.length || 0})</span>
          </div>

          <div className="space-y-3">
            {(databases || []).map((db) => (
              <div key={db.id} className="glass-panel rounded-xl p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-display font-bold text-white text-sm">{db.name}</span>
                  <span className="font-mono text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    {db.engine}
                  </span>
                </div>
                <div className="text-xs text-slate-400 font-mono">Type: {db.type}</div>
                <p className="text-xs text-slate-300 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800 font-mono">
                  {db.schema_overview}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Architecture Decision Records (ADRs) with Grounded RAG Citations */}
      {adrs && adrs.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
            <h3>Architecture Decision Records (ADRs)</h3>
            <span className="text-xs font-mono text-slate-400">({adrs.length})</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {adrs.map((adr) => (
              <div key={adr.id} className="glass-panel rounded-xl p-5 space-y-3 border-l-4 border-l-brand-500">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold text-brand-400 px-2.5 py-0.5 rounded bg-brand-500/10 border border-brand-500/20">
                      {adr.id}
                    </span>
                    <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      {adr.status}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">
                    Confidence: {Math.round((adr.confidence || 0.9) * 100)}%
                  </span>
                </div>

                <h4 className="font-display font-bold text-white text-base">{adr.title}</h4>

                <div className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded-lg border border-slate-800 space-y-1.5">
                  <div><strong className="text-brand-300">Decision: </strong>{adr.decision}</div>
                  <div><strong className="text-slate-400">Rationale: </strong>{adr.rationale}</div>
                  {adr.consequences && (
                    <div className="text-slate-400 pt-1 border-t border-slate-800"><strong className="text-amber-400">Trade-offs & Consequences: </strong>{adr.consequences}</div>
                  )}
                </div>

                {/* Linked Requirements and RAG Evidence Citations */}
                <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-800 text-xs">
                  {adr.requirement_ids && adr.requirement_ids.length > 0 && (
                    <div className="flex items-center space-x-1">
                      <span className="text-slate-400 font-mono text-[11px]">FRs:</span>
                      {adr.requirement_ids.map((fr) => (
                        <span key={fr} className="font-mono text-[10px] text-brand-300 bg-brand-500/10 px-1.5 py-0.5 rounded border border-brand-500/20">
                          {fr}
                        </span>
                      ))}
                    </div>
                  )}
                  {adr.evidence_ids && adr.evidence_ids.length > 0 && (
                    <div className="flex items-center space-x-1">
                      <span className="text-slate-400 font-mono text-[11px]">RAG Evidence:</span>
                      {adr.evidence_ids.map((ev) => (
                        <span key={ev} className="font-mono text-[10px] text-accent-cyan bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/20 font-bold">
                          {ev}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strategies Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel rounded-xl p-5 space-y-2">
          <div className="flex items-center space-x-2 text-brand-400 font-bold text-sm">
            <Shield className="w-4 h-4" />
            <h4>Security Strategy</h4>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">{security_strategy}</p>
        </div>

        <div className="glass-panel rounded-xl p-5 space-y-2">
          <div className="flex items-center space-x-2 text-amber-400 font-bold text-sm">
            <Zap className="w-4 h-4" />
            <h4>Scalability Strategy</h4>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">{scalability_strategy}</p>
        </div>

        <div className="glass-panel rounded-xl p-5 space-y-2">
          <div className="flex items-center space-x-2 text-accent-cyan font-bold text-sm">
            <Server className="w-4 h-4" />
            <h4>Deployment Topology</h4>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">{deployment_topology}</p>
        </div>
      </div>
    </div>
  );
}
