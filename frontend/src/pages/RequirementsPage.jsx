import React, { useState } from 'react';
import { 
  Layers, 
  Filter, 
  Users, 
  Shield, 
  AlertTriangle, 
  CheckSquare, 
  Search, 
  Calculator, 
  TrendingUp, 
  Award, 
  ArrowUpDown,
  Sparkles,
  Info
} from 'lucide-react';

export default function RequirementsPage({ blueprint, onSimulateImpact }) {
  const [filterPriority, setFilterPriority] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('rice'); // 'rice', 'moscow', 'id'
  const [showRiceExplainer, setShowRiceExplainer] = useState(false);

  if (!blueprint?.requirements) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center text-slate-400">
        <Layers className="w-12 h-12 mx-auto mb-3 text-slate-600" />
        <p>No requirements loaded. Please generate or load a blueprint on the Dashboard.</p>
      </div>
    );
  }

  const { 
    project_name, 
    project_description, 
    stakeholders, 
    functional_requirements, 
    non_functional_requirements, 
    constraints, 
    ambiguities, 
    assumptions 
  } = blueprint.requirements;

  const filteredFRs = (functional_requirements || []).filter((fr) => {
    const matchesPriority = filterPriority === 'ALL' || fr.priority?.toLowerCase() === filterPriority.toLowerCase();
    const matchesSearch = fr.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      fr.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      fr.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesPriority && matchesSearch;
  });

  const sortedFRs = [...filteredFRs].sort((a, b) => {
    if (sortBy === 'rice') {
      const scoreA = a.rice?.score ?? 0;
      const scoreB = b.rice?.score ?? 0;
      return scoreB - scoreA;
    }
    if (sortBy === 'moscow') {
      const priorityOrder = { must: 4, should: 3, could: 2, "won't": 1, wont: 1 };
      const pA = priorityOrder[a.priority?.toLowerCase()] || 0;
      const pB = priorityOrder[b.priority?.toLowerCase()] || 0;
      return pB - pA;
    }
    return a.id.localeCompare(b.id);
  });

  const getPriorityBadgeClass = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'must':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      case 'should':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'could':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
      case "won't":
      case 'wont':
        return 'bg-slate-700 text-slate-400 border-slate-600';
      default:
        return 'bg-brand-500/20 text-brand-300 border-brand-500/30';
    }
  };

  const getImpactBadgeClass = (impact) => {
    if (impact >= 3.0) return 'text-purple-300 bg-purple-500/10 border-purple-500/20';
    if (impact >= 2.0) return 'text-cyan-300 bg-cyan-500/10 border-cyan-500/20';
    if (impact >= 1.0) return 'text-emerald-300 bg-emerald-500/10 border-emerald-500/20';
    return 'text-slate-400 bg-slate-800 border-slate-700';
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Overview Banner */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex items-center space-x-3 text-brand-400 text-xs font-mono mb-2">
          <Layers className="w-4 h-4" />
          <span>Module 1 — Software Requirements Specification (SRS)</span>
        </div>
        <h2 className="text-2xl font-display font-bold text-white mb-2">{project_name}</h2>
        <p className="text-sm text-slate-300 leading-relaxed max-w-4xl">{project_description}</p>
      </div>

      {/* DUAL PRIORITIZATION ENGINE BANNER (MoSCoW + RICE) */}
      <div className="glass-panel rounded-2xl p-5 border-l-4 border-l-amber-400 bg-slate-900/60 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-sm">
            <Calculator className="w-4 h-4 text-amber-400" />
            <h3>Dual Prioritization Engine: Qualitative MoSCoW & Quantitative RICE Framework</h3>
          </div>
          <button
            onClick={() => setShowRiceExplainer(!showRiceExplainer)}
            className="flex items-center space-x-1.5 text-xs text-amber-300 hover:text-white font-mono bg-amber-500/10 hover:bg-amber-500/20 px-2.5 py-1 rounded-lg border border-amber-500/20 transition self-start sm:self-auto"
          >
            <Info className="w-3.5 h-3.5" />
            <span>{showRiceExplainer ? 'Hide Formula Details' : 'View RICE Formula'}</span>
          </button>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          Requirements are ranked using two industry-standard methodologies: <strong>Qualitative MoSCoW</strong> (Must, Should, Could, Won't) for contract scope boundaries, and the <strong>Quantitative RICE Algorithm</strong> (Reach × Impact × Confidence / Effort) for mathematically objective backlog ranking.
        </p>

        {showRiceExplainer && (
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-3 text-xs animate-in fade-in">
            <div className="flex items-center space-x-2 font-mono text-amber-400 text-sm font-bold">
              <span>Mathematical Formula:</span>
              <span className="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300">
                RICE Score = (Reach × Impact × Confidence) / Effort
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <span className="font-mono font-bold text-cyan-400 block mb-0.5">1. Reach (R)</span>
                <span className="text-slate-300 text-[11px]">Users or transactions affected in a given timeframe (e.g. 5,000 customers/mo).</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <span className="font-mono font-bold text-purple-400 block mb-0.5">2. Impact (I)</span>
                <span className="text-slate-300 text-[11px]">Standardized goal contribution: 3.0 (Massive), 2.0 (High), 1.0 (Medium), 0.5 (Low), 0.25 (Minimal).</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <span className="font-mono font-bold text-emerald-400 block mb-0.5">3. Confidence (C)</span>
                <span className="text-slate-300 text-[11px]">Certainty ratio in estimation data: 100% (High), 80% (Medium), 50% (Low/Moonshot).</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <span className="font-mono font-bold text-amber-400 block mb-0.5">4. Effort (E)</span>
                <span className="text-slate-300 text-[11px]">Time required from product, design, and engineering (in person-months or team-weeks).</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Stakeholders Grid */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
          <Users className="w-5 h-5 text-accent-cyan" />
          <h3>Identified Stakeholders</h3>
          <span className="text-xs font-mono text-slate-400">({stakeholders?.length || 0})</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {(stakeholders || []).map((st) => (
            <div key={st.id} className="glass-panel rounded-xl p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-accent-cyan px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
                  {st.id}
                </span>
                <span className="text-xs font-bold text-white">{st.name}</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{st.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Functional Requirements with Dual Filter & Sort Toolbar */}
      <div className="space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <CheckSquare className="w-5 h-5 text-brand-400" />
            <h3>Functional Requirements (FR)</h3>
            <span className="text-xs font-mono text-slate-400">({sortedFRs.length})</span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Search Input */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                placeholder="Search FRs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="text-xs bg-slate-900 border border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
              />
            </div>

            {/* Sort Selector */}
            <div className="flex items-center space-x-1 bg-slate-900 border border-slate-700 rounded-lg p-0.5 text-xs">
              <span className="text-[11px] text-slate-400 px-2 flex items-center space-x-1">
                <ArrowUpDown className="w-3 h-3" />
                <span>Sort:</span>
              </span>
              <button
                onClick={() => setSortBy('rice')}
                className={`px-2.5 py-1 rounded-md transition font-mono ${
                  sortBy === 'rice' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'
                }`}
                title="Sort by RICE Score (Highest to Lowest)"
              >
                RICE Score
              </button>
              <button
                onClick={() => setSortBy('moscow')}
                className={`px-2.5 py-1 rounded-md transition font-mono ${
                  sortBy === 'moscow' ? 'bg-brand-600 text-white font-medium' : 'text-slate-400 hover:text-white'
                }`}
                title="Sort by MoSCoW Priority"
              >
                MoSCoW
              </button>
              <button
                onClick={() => setSortBy('id')}
                className={`px-2.5 py-1 rounded-md transition font-mono ${
                  sortBy === 'id' ? 'bg-slate-700 text-white font-medium' : 'text-slate-400 hover:text-white'
                }`}
                title="Sort by Requirement ID"
              >
                ID
              </button>
            </div>

            {/* MoSCoW Filter */}
            <div className="flex items-center bg-slate-900 border border-slate-700 rounded-lg p-0.5 text-xs">
              {['ALL', 'Must', 'Should', 'Could'].map((p) => (
                <button
                  key={p}
                  onClick={() => setFilterPriority(p)}
                  className={`px-2.5 py-1 rounded-md transition ${
                    filterPriority === p ? 'bg-brand-600 text-white font-medium' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sortedFRs.map((fr) => {
            const rice = fr.rice;
            return (
              <div key={fr.id} className="glass-panel slice-card rounded-xl p-5 space-y-3.5 flex flex-col justify-between">
                <div className="space-y-3">
                  {/* Card Header with Badges */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center space-x-2">
                      <span className="badge-id text-xs text-brand-400 px-2 py-0.5 rounded bg-brand-500/10 border border-brand-500/20 font-mono font-bold">
                        {fr.id}
                      </span>
                      <h4 className="font-display font-semibold text-white text-sm">{fr.title}</h4>
                    </div>

                    <div className="flex items-center space-x-1.5 flex-shrink-0">
                      {/* MoSCoW Badge */}
                      <span className={`text-[11px] px-2.5 py-0.5 rounded-full border font-mono font-medium ${getPriorityBadgeClass(fr.priority)}`}>
                        {fr.priority}
                      </span>

                      {/* RICE Score Badge */}
                      {rice && (
                        <span className="text-[11px] px-2.5 py-0.5 rounded-full font-mono font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 flex items-center space-x-1">
                          <Award className="w-3 h-3 text-amber-400" />
                          <span>RICE: {rice.score.toLocaleString()}</span>
                          {rice.rank && <span className="text-amber-400/80">#{rice.rank}</span>}
                        </span>
                      )}
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed">{fr.description}</p>

                  {/* RICE QUANTITATIVE PARAMETERS BREAKDOWN */}
                  {rice && (
                    <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2">
                      <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 border-b border-slate-800/80 pb-1.5">
                        <span className="flex items-center space-x-1 text-amber-300/90 font-semibold">
                          <Calculator className="w-3 h-3 text-amber-400" />
                          <span>RICE Framework Metrics:</span>
                        </span>
                        <span className="text-slate-400 font-mono">
                          Rank #{rice.rank || 1} in Backlog
                        </span>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                        {/* Reach */}
                        <div className="p-1.5 rounded bg-slate-900 border border-slate-800">
                          <span className="text-slate-500 text-[10px] block font-mono">REACH</span>
                          <span className="text-cyan-300 font-bold font-mono">{rice.reach.toLocaleString()}</span>
                          <span className="text-slate-500 text-[9px] block">users/mo</span>
                        </div>

                        {/* Impact */}
                        <div className="p-1.5 rounded bg-slate-900 border border-slate-800">
                          <span className="text-slate-500 text-[10px] block font-mono">IMPACT</span>
                          <span className="text-purple-300 font-bold font-mono">{rice.impact}</span>
                          <span className="text-slate-400 text-[9px] block truncate">
                            {rice.impact >= 3 ? 'Massive' : rice.impact >= 2 ? 'High' : 'Medium'}
                          </span>
                        </div>

                        {/* Confidence */}
                        <div className="p-1.5 rounded bg-slate-900 border border-slate-800">
                          <span className="text-slate-500 text-[10px] block font-mono">CONFIDENCE</span>
                          <span className="text-emerald-300 font-bold font-mono">
                            {Math.round(rice.confidence > 1 ? rice.confidence : rice.confidence * 100)}%
                          </span>
                          <span className="text-slate-400 text-[9px] block">
                            {rice.confidence >= 0.8 ? 'High' : 'Medium'}
                          </span>
                        </div>

                        {/* Effort */}
                        <div className="p-1.5 rounded bg-slate-900 border border-slate-800">
                          <span className="text-slate-500 text-[10px] block font-mono">EFFORT</span>
                          <span className="text-amber-300 font-bold font-mono">{rice.effort}</span>
                          <span className="text-slate-500 text-[9px] block">pers-mo</span>
                        </div>
                      </div>

                      <div className="text-[10px] font-mono text-slate-400 pt-1 flex items-center justify-between border-t border-slate-850">
                        <span>Formula: ({rice.reach.toLocaleString()} × {rice.impact} × {Math.round(rice.confidence > 1 ? rice.confidence : rice.confidence * 100)}%) / {rice.effort}</span>
                        <span className="text-amber-300 font-bold font-mono">= {rice.score.toLocaleString()} pts</span>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Card Footer: Stakeholders + Impact Action */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-800/80">
                  {fr.stakeholders && fr.stakeholders.length > 0 ? (
                    <div className="flex items-center space-x-1.5 text-[11px] text-slate-400">
                      <span className="text-slate-500 font-mono">Stakeholders:</span>
                      {fr.stakeholders.map((st) => (
                        <span key={st} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">
                          {st}
                        </span>
                      ))}
                    </div>
                  ) : <div />}
                  
                  {onSimulateImpact && (
                    <button
                      onClick={() => onSimulateImpact(fr.id)}
                      className="inline-flex items-center space-x-1 text-[11px] font-medium text-rose-400 hover:text-rose-300 px-2 py-1 rounded bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 transition"
                      title="Simulate downstream change blast radius and selective regeneration"
                    >
                      <span>⚡ Simulate Impact</span>
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Non-Functional Requirements Grid */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
          <Shield className="w-5 h-5 text-emerald-400" />
          <h3>Non-Functional Requirements (NFR)</h3>
          <span className="text-xs font-mono text-slate-400">({non_functional_requirements?.length || 0})</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {(non_functional_requirements || []).map((nfr) => (
            <div key={nfr.id} className="glass-panel rounded-xl p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                  {nfr.id}
                </span>
                <span className="text-xs font-bold text-white uppercase tracking-wider">{nfr.category}</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{nfr.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Ambiguities & Clarification Prompts */}
      {ambiguities && ambiguities.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <h3>Detected Ambiguities & Clarification Prompts</h3>
            <span className="text-xs font-mono text-slate-400">({ambiguities.length})</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {ambiguities.map((amb, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 space-y-2">
                <div className="text-xs text-amber-300 font-semibold flex items-center space-x-1.5">
                  <span>Ambiguity:</span>
                  <span className="text-white font-normal">{amb.ambiguity}</span>
                </div>
                <div className="text-xs text-slate-300 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                  <span className="text-amber-400 font-mono">Suggested Clarification: </span>
                  {amb.possible_clarification}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
