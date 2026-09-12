import React from 'react';
import { Sparkles, Cpu, CheckCircle2, Clock, GitCommit, Milestone as MilestoneIcon } from 'lucide-react';

export default function ProjectPlanPage({ blueprint }) {
  if (!blueprint?.project_plan) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center text-slate-400">
        <Sparkles className="w-12 h-12 mx-auto mb-3 text-slate-600" />
        <p>No project plan loaded. Please generate a blueprint first.</p>
      </div>
    );
  }

  const { modules, tasks, milestones, roadmap } = blueprint.project_plan;
  const totalHours = (tasks || []).reduce((acc, t) => acc + (t.estimated_hours || 0), 0);

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-brand-400 text-xs font-mono mb-1">
            <Sparkles className="w-4 h-4" />
            <span>Module 2 — Engineering Project Plan & Work Breakdown Structure (WBS)</span>
          </div>
          <h2 className="text-2xl font-display font-bold text-white">Execution Plan & Scheduling</h2>
        </div>
        <div className="flex items-center space-x-4 bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <div>
            <div className="text-[11px] text-slate-400">Total Effort</div>
            <div className="text-xl font-bold font-mono text-amber-400">{totalHours} hrs</div>
          </div>
          <div className="w-px h-8 bg-slate-700"></div>
          <div>
            <div className="text-[11px] text-slate-400">Total Tasks</div>
            <div className="text-xl font-bold font-mono text-emerald-400">{tasks?.length || 0}</div>
          </div>
        </div>
      </div>

      {/* Modules Subsystems */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
          <Cpu className="w-5 h-5 text-purple-400" />
          <h3>Logical Subsystems / Modules</h3>
          <span className="text-xs font-mono text-slate-400">({modules?.length || 0})</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(modules || []).map((m) => (
            <div key={m.id} className="glass-panel rounded-xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-purple-400 px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20">
                  {m.id}
                </span>
                <h4 className="font-display font-bold text-white text-sm">{m.name}</h4>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{m.description}</p>
              
              <div className="space-y-1.5 pt-2 border-t border-slate-800 text-[11px]">
                <div className="flex items-center space-x-1">
                  <span className="text-slate-500 font-mono">FRs:</span>
                  {(m.requirement_ids || []).map((r) => (
                    <span key={r} className="px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 font-mono">{r}</span>
                  ))}
                </div>
                <div className="flex items-center space-x-1">
                  <span className="text-slate-500 font-mono">Tasks:</span>
                  {(m.task_ids || []).map((t) => (
                    <span key={t} className="px-1.5 py-0.2 rounded bg-brand-500/10 text-brand-300 font-mono">{t}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Development Tasks WBS Table */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <h3>Task Breakdown & Dependency Scheduling</h3>
        </div>

        <div className="glass-panel rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/90 text-slate-400 font-mono border-b border-slate-800 uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="px-4 py-3">Task ID</th>
                  <th className="px-4 py-3">Task Title & Description</th>
                  <th className="px-4 py-3">Traced FRs</th>
                  <th className="px-4 py-3">Dependencies</th>
                  <th className="px-4 py-3 text-right">Est. Hours</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {(tasks || []).map((t) => (
                  <tr key={t.id} className="hover:bg-slate-800/30 transition">
                    <td className="px-4 py-3 font-mono font-bold text-emerald-400 whitespace-nowrap">
                      {t.id}
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-semibold text-white text-xs mb-0.5">{t.title}</div>
                      <div className="text-[11px] text-slate-400 max-w-xl">{t.description}</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex flex-wrap gap-1">
                        {(t.requirement_ids || []).map((r) => (
                          <span key={r} className="px-1.5 py-0.5 rounded bg-brand-500/10 border border-brand-500/20 text-brand-300 font-mono text-[10px]">
                            {r}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap font-mono text-[11px]">
                      {t.dependencies && t.dependencies.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {t.dependencies.map((dep) => (
                            <span key={dep} className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[10px]">
                              {dep}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-slate-500">None (Root)</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right font-mono font-bold text-amber-400 whitespace-nowrap">
                      {t.estimated_hours}h
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Milestones & Roadmap */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <MilestoneIcon className="w-5 h-5 text-accent-cyan" />
            <h3>Project Milestones</h3>
          </div>
          <div className="space-y-3">
            {(milestones || []).map((m) => (
              <div key={m.id} className="glass-panel rounded-xl p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-accent-cyan px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
                    {m.id}
                  </span>
                  <span className="text-xs font-bold text-white">{m.name}</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{m.description}</p>
                <div className="flex items-center space-x-1 pt-1 text-[11px] text-slate-400">
                  <span className="text-slate-500 font-mono">Deliverables:</span>
                  {(m.task_ids || []).map((t) => (
                    <span key={t} className="px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 font-mono">{t}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <GitCommit className="w-5 h-5 text-brand-400" />
            <h3>Phased Development Roadmap</h3>
          </div>
          <div className="glass-panel rounded-2xl p-5 space-y-4">
            {(roadmap || []).map((phase, idx) => (
              <div key={idx} className="flex items-start space-x-3">
                <div className="w-6 h-6 rounded-full bg-brand-600/30 border border-brand-500 text-brand-300 flex items-center justify-center font-mono text-xs font-bold shrink-0 mt-0.5">
                  {idx + 1}
                </div>
                <div className="text-xs text-slate-200 font-medium pt-1">
                  {phase}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
