import React, { useState } from 'react';
import {
  Database,
  Server,
  Cpu,
  Shield,
  Zap,
  Layers,
  Globe,
  Code,
  ArrowRight,
  CheckCircle,
  BookOpen,
  Sparkles,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';

export default function ArchitecturePage({ blueprint }) {
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [selectedTechStack, setSelectedTechStack] = useState(null);

  if (!blueprint?.architecture) {
    return (
      <div className="glass-panel rounded-2xl p-12 text-center text-slate-400">
        <Database className="w-12 h-12 mx-auto mb-3 text-slate-600" />
        <p>No architecture blueprint loaded. Please generate a blueprint first.</p>
      </div>
    );
  }

  const {
    architecture_style,
    overview,
    containers,
    components,
    apis,
    databases,
    adrs,
    tech_stack_rationale,
    security_strategy,
    scalability_strategy,
    deployment_topology
  } = blueprint.architecture;

  // Comprehensive default tech stack justifications if not yet populated
  const effectiveTechStack = (tech_stack_rationale && tech_stack_rationale.length > 0) ? tech_stack_rationale : [
    {
      layer: "Backend Framework",
      technology: "FastAPI (Python 3.11)",
      category: "Application Layer",
      decision_rationale: "High-performance asynchronous execution engine via ASGI (Starlette/Uvicorn), strict type validation via Pydantic v2, and automatic OpenAPI schema generation conforming to IEEE/ISO API standards.",
      pros: [
        "Asynchronous non-blocking event loop handling high concurrent I/O",
        "Native Pydantic v2 schema validation with sub-millisecond serialization",
        "Automated interactive Swagger & ReDoc API contract generation"
      ],
      tradeoffs: "Requires asynchronous database driver discipline (e.g. asyncpg/SQLAlchemy async) to avoid event loop thread blocking.",
      rag_citation: "API-001"
    },
    {
      layer: "Relational Persistence",
      technology: "PostgreSQL 16",
      category: "Database Tier",
      decision_rationale: "Enterprise-grade relational storage chosen for strict ACID compliance, MVCC write concurrency, JSONB document querying capabilities, and mature row-level security.",
      pros: [
        "Rock-solid transactional integrity for core domain entity graphs",
        "Multi-Version Concurrency Control (MVCC) without table-locking overhead",
        "Native JSONB indexing for semi-structured metadata"
      ],
      tradeoffs: "Requires connection pooling proxy (PgBouncer) under high concurrent microservice connection spikes.",
      rag_citation: "DATA-001"
    },
    {
      layer: "Cache & Performance Tier",
      technology: "Redis 7 / In-Memory LRU",
      category: "Caching Tier",
      decision_rationale: "Sub-millisecond key-value caching layer implementing the Cache-Aside pattern with deterministic SHA-256 key invalidation, shielding database connections from thundering herd spikes.",
      pros: [
        "In-memory sub-millisecond read/write latencies",
        "Native TTL expiration and LRU/LFU memory eviction policies",
        "Distributed atomic operations for rate-limiting and session locks"
      ],
      tradeoffs: "Volatile memory store requiring proactive eviction policies and cache invalidation consistency management.",
      rag_citation: "SCALE-001"
    },
    {
      layer: "Vector Knowledge Engine",
      technology: "Qdrant Vector Database",
      category: "AI / RAG Tier",
      decision_rationale: "High-throughput vector similarity search engine utilizing HNSW indexing with scalar quantization and rich payload metadata filtering for evidence retrieval.",
      pros: [
        "Sub-millisecond cosine distance approximate nearest neighbor (ANN) search",
        "Filterable metadata payloads enabling section-level breadcrumb extraction",
        "Seamless local embedded/Docker operation with ACID collection snapshots"
      ],
      tradeoffs: "Dense vector index memory footprint grows linearly with high-dimensional embedding spaces.",
      rag_citation: "DATA-001"
    },
    {
      layer: "Frontend UI Architecture",
      technology: "React 18 & Vite",
      category: "Presentation Tier",
      decision_rationale: "Component-driven reactive single-page architecture with state-driven rendering, client-side caching, and rapid hot module reloading (HMR) for responsive operator interfaces.",
      pros: [
        "Virtual DOM differential reconciliation minimizing DOM reflows",
        "Component reusability adhering to Atomic Design principles",
        "Sub-second build bundling via esbuild and Vite rollup engine"
      ],
      tradeoffs: "Client-side single-page application requires bundle code-splitting and asset caching for optimal first-contentful paint.",
      rag_citation: "ARCH-001"
    },
    {
      layer: "Security & Access Control",
      technology: "OAuth 2.1 & JWT Bearer Tokens",
      category: "Security Tier",
      decision_rationale: "Stateless cryptographic token authorization adhering to RFC 6749/RFC 9068 with HMAC-SHA256 signature verification, eliminating stateful session database lookups across distributed service nodes.",
      pros: [
        "Stateless signature verification across independent backend microservices",
        "Fine-grained role-based access control (RBAC) claims in token payloads",
        "Zero-trust architecture compatible with token rotation and short TTLs"
      ],
      tradeoffs: "Stateless tokens cannot be revoked instantly without distributed Redis blacklist cache lookups.",
      rag_citation: "SEC-001"
    }
  ];

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

      {/* TECH STACK SELECTION & LITERATURE JUSTIFICATIONS */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <Sparkles className="w-5 h-5 text-amber-400" />
            <h3>Tech Stack Selection & Literature Justifications</h3>
            <span className="text-xs font-mono text-slate-400">({effectiveTechStack.length} Tiers)</span>
          </div>
          <span className="text-xs font-mono text-amber-400/90 bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20">
            Why Each Technology Was Chosen
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {effectiveTechStack.map((item, idx) => (
            <div
              key={idx}
              className="glass-panel rounded-xl p-5 space-y-3.5 border-t-2 border-t-amber-400/80 hover:border-slate-600 transition flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                    {item.layer}
                  </span>
                  {item.rag_citation && (
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-accent-cyan border border-cyan-500/20">
                      [{item.rag_citation}] Literature
                    </span>
                  )}
                </div>

                <div className="flex items-baseline justify-between">
                  <h4 className="font-display font-bold text-white text-base">{item.technology}</h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                    {item.category || 'Framework'}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300 leading-relaxed space-y-1.5">
                  <div className="text-[11px] font-semibold text-amber-300/90 font-mono flex items-center space-x-1">
                    <span>Why Chosen:</span>
                  </div>
                  <p>{item.decision_rationale}</p>
                </div>
              </div>

              <div className="space-y-2.5 pt-2 border-t border-slate-800 text-xs">
                {item.pros && item.pros.length > 0 && (
                  <div>
                    <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-1">
                      Key Technical Advantages:
                    </div>
                    <ul className="space-y-1">
                      {item.pros.map((pro, pIdx) => (
                        <li key={pIdx} className="flex items-start space-x-1.5 text-slate-300 text-[11px]">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                          <span>{pro}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {item.tradeoffs && (
                  <div className="p-2.5 rounded-lg bg-amber-500/5 border border-amber-500/20 text-[11px] text-amber-200/90">
                    <span className="font-semibold text-amber-400 font-mono">Trade-offs Considered: </span>
                    <span>{item.tradeoffs}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
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

                <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-400 pt-1 border-t border-slate-800">
                  <span>Owner: <strong className="text-slate-300">{api.component_id}</strong></span>
                  <span>Requirements: <strong className="text-brand-300">{(api.requirement_ids || []).join(', ')}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Databases & Storage */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
            <Database className="w-5 h-5 text-brand-400" />
            <h3>Data Persistence & Caching</h3>
            <span className="text-xs font-mono text-slate-400">({databases?.length || 0})</span>
          </div>

          <div className="space-y-3">
            {(databases || []).map((db) => (
              <div key={db.id} className="glass-panel rounded-xl p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Database className="w-4 h-4 text-brand-400" />
                    <span className="font-bold text-white text-sm">{db.name}</span>
                    <span className="text-xs text-slate-400 font-mono">({db.engine})</span>
                  </div>
                  <span className="font-mono text-[10px] text-slate-500">{db.id}</span>
                </div>
                <div className="text-xs font-mono text-slate-300 bg-slate-900/60 p-2 rounded border border-slate-800">
                  {db.schema_overview}
                </div>
                <div className="text-[11px] font-mono text-slate-400">
                  Connected Components: <strong className="text-slate-300">{(db.component_ids || []).join(', ')}</strong>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Architecture Decision Records (ADRs) */}
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
