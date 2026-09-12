import React, { useState, useEffect } from 'react';
import { GitCommit, Search, Filter, Layers, CheckCircle2, Cpu, Globe, Database } from 'lucide-react';
import { getTraceability } from '../services/api';

export default function TraceabilityPage({ blueprint }) {
  const [traceData, setTraceData] = useState(null);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchTraceability = async () => {
    if (!blueprint?.project_id) return;
    setLoading(true);
    try {
      const data = await getTraceability(blueprint.project_id);
      setTraceData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTraceability();
  }, [blueprint?.project_id, blueprint?.version]);

  if (!blueprint?.requirements) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center text-slate-400">
        <GitCommit className="w-12 h-12 mx-auto mb-3 text-slate-600" />
        <p>No blueprint loaded. Please generate or load a blueprint first.</p>
      </div>
    );
  }

  const { functional_requirements } = blueprint.requirements;
  const { modules, tasks, milestones } = blueprint.project_plan || {};
  const { components, apis } = blueprint.architecture || {};

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex items-center space-x-2 text-brand-400 text-xs font-mono mb-1">
          <GitCommit className="w-4 h-4" />
          <span>Multi-Tier Traceability Matrix & Graph Visualizer</span>
        </div>
        <h2 className="text-2xl font-display font-bold text-white mb-2">End-to-End Requirement Traceability</h2>
        <p className="text-sm text-slate-300 leading-relaxed max-w-4xl">
          Bidirectional dependency graph: <span className="text-accent-cyan font-mono">Stakeholder</span> &rarr; <span className="text-brand-400 font-mono">FR</span> &rarr; <span className="text-purple-400 font-mono">Module</span> &rarr; <span className="text-emerald-400 font-mono">Task</span> &rarr; <span className="text-rose-400 font-mono">Component</span> &rarr; <span className="text-amber-400 font-mono">API / DB</span> &rarr; <span className="text-cyan-300 font-mono">Milestone</span>.
        </p>
      </div>

      {/* Interactive Traceability Matrix Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <Layers className="w-5 h-5 text-brand-400" />
            <h3>Requirement Traceability Matrix (RTM)</h3>
            <span className="text-xs font-mono text-slate-400">({functional_requirements?.length || 0} Chains)</span>
          </div>
        </div>

        <div className="space-y-4">
          {(functional_requirements || []).map((fr) => {
            const linkedModules = (modules || []).filter((m) => (m.requirement_ids || []).includes(fr.id));
            const linkedTasks = (tasks || []).filter((t) => (t.requirement_ids || []).includes(fr.id));
            const linkedComps = (components || []).filter((c) => (c.requirement_ids || []).includes(fr.id));
            const linkedApis = (apis || []).filter((a) => (a.requirement_ids || []).includes(fr.id));

            return (
              <div key={fr.id} className="glass-panel rounded-2xl p-5 space-y-4 hover:border-slate-600 transition">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div className="flex items-center space-x-3">
                    <span className="font-mono text-xs font-bold text-brand-400 px-2.5 py-1 rounded-lg bg-brand-500/10 border border-brand-500/20">
                      {fr.id}
                    </span>
                    <h4 className="font-display font-bold text-white text-sm">{fr.title}</h4>
                  </div>
                  <span className="text-xs font-mono text-slate-400 bg-slate-900 px-2.5 py-0.5 rounded border border-slate-800 self-start sm:self-auto">
                    Priority: {fr.priority}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
                  {/* Module */}
                  <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
                    <div className="text-[11px] text-purple-400 font-mono flex items-center space-x-1">
                      <Cpu className="w-3.5 h-3.5" />
                      <span>Parent Subsystems</span>
                    </div>
                    {linkedModules.length > 0 ? (
                      linkedModules.map((m) => (
                        <div key={m.id} className="text-white font-medium">{m.id}: {m.name}</div>
                      ))
                    ) : (
                      <div className="text-slate-500 italic">No direct module</div>
                    )}
                  </div>

                  {/* Tasks */}
                  <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
                    <div className="text-[11px] text-emerald-400 font-mono flex items-center space-x-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Development Tasks</span>
                    </div>
                    {linkedTasks.length > 0 ? (
                      linkedTasks.map((t) => (
                        <div key={t.id} className="text-white font-medium">{t.id}: {t.title.slice(0, 24)} ({t.estimated_hours}h)</div>
                      ))
                    ) : (
                      <div className="text-rose-400 italic">Untraced task</div>
                    )}
                  </div>

                  {/* Architecture Components */}
                  <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
                    <div className="text-[11px] text-rose-400 font-mono flex items-center space-x-1">
                      <Database className="w-3.5 h-3.5" />
                      <span>Architecture Comps</span>
                    </div>
                    {linkedComps.length > 0 ? (
                      linkedComps.map((c) => (
                        <div key={c.id} className="text-white font-medium">{c.id}: {c.name}</div>
                      ))
                    ) : (
                      <div className="text-slate-500 italic">No component mapped</div>
                    )}
                  </div>

                  {/* APIs */}
                  <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
                    <div className="text-[11px] text-amber-400 font-mono flex items-center space-x-1">
                      <Globe className="w-3.5 h-3.5" />
                      <span>API Endpoints</span>
                    </div>
                    {linkedApis.length > 0 ? (
                      linkedApis.map((a) => (
                        <div key={a.id} className="text-white font-mono text-[11px]">{a.method} {a.endpoint}</div>
                      ))
                    ) : (
                      <div className="text-slate-500 italic">Internal service</div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
