import React, { useState, useEffect } from 'react';
import { 
  BookOpen, ShieldCheck, Cpu, ExternalLink, CheckCircle, 
  AlertCircle, Database, Search, RefreshCw, Layers, Terminal, Compass, FileText
} from 'lucide-react';
import { getRagDocuments, getRagChunks, getQdrantInfo, reindexRag } from '../services/api';

export default function RAGEvidencePage({ blueprint }) {
  const [activeTab, setActiveTab] = useState('recommendations');
  const [documents, setDocuments] = useState([]);
  const [chunks, setChunks] = useState([]);
  const [qdrantInfo, setQdrantInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [reindexing, setReindexing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDocId, setSelectedDocId] = useState(null);

  const recommendations = blueprint?.rag_recommendations || [];

  useEffect(() => {
    loadKnowledgeBaseData();
  }, []);

  const loadKnowledgeBaseData = async () => {
    try {
      setLoading(true);
      const [docsData, qdrantData, chunksData] = await Promise.allSettled([
        getRagDocuments(),
        getQdrantInfo(),
        getRagChunks()
      ]);

      if (docsData.status === 'fulfilled') setDocuments(docsData.value || []);
      if (qdrantData.status === 'fulfilled') setQdrantInfo(qdrantData.value || null);
      if (chunksData.status === 'fulfilled') setChunks(chunksData.value || []);
    } catch (err) {
      console.error('Failed to load RAG knowledge data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReindex = async () => {
    try {
      setReindexing(true);
      await reindexRag();
      await loadKnowledgeBaseData();
    } catch (err) {
      console.error('Reindex failed:', err);
    } finally {
      setReindexing(false);
    }
  };

  const filteredDocs = documents.filter(doc => {
    const q = searchQuery.toLowerCase();
    return (
      doc.title.toLowerCase().includes(q) ||
      doc.document_id.toLowerCase().includes(q) ||
      doc.category.toLowerCase().includes(q) ||
      (doc.keywords && doc.keywords.some(k => k.toLowerCase().includes(q)))
    );
  });

  const filteredChunks = chunks.filter(chunk => {
    if (selectedDocId && chunk.document_id !== selectedDocId) return false;
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      (chunk.title && chunk.title.toLowerCase().includes(q)) ||
      (chunk.section && chunk.section.toLowerCase().includes(q)) ||
      (chunk.excerpt && chunk.excerpt.toLowerCase().includes(q)) ||
      (chunk.keywords && chunk.keywords.some(k => k.toLowerCase().includes(q)))
    );
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-200">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex items-center space-x-2 text-brand-400 text-xs font-mono mb-1">
          <BookOpen className="w-4 h-4" />
          <span>Module 4 — Academic Retrieval-Augmented Generation (RAG) & Vector Engine</span>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-display font-bold text-white mb-1">Architectural Knowledge Base & Vector Grounding</h2>
            <p className="text-sm text-slate-300 leading-relaxed max-w-4xl">
              High-depth architectural literature indexed using Hierarchical Markdown Chunking with Context Breadcrumbs into Qdrant vector database.
            </p>
          </div>
          <div className="flex items-center space-x-2 self-start sm:self-auto">
            <button
              onClick={handleReindex}
              disabled={reindexing}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono border border-slate-700 transition"
              title="Re-read markdown files and re-index into vector store"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${reindexing ? 'animate-spin text-brand-400' : ''}`} />
              <span>{reindexing ? 'Reindexing...' : 'Reindex Vectors'}</span>
            </button>
            <a
              href="http://localhost:6333/dashboard"
              target="_blank"
              rel="noreferrer"
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-brand-500/20 hover:bg-brand-500/30 text-brand-300 text-xs font-mono border border-brand-500/30 transition"
            >
              <Database className="w-3.5 h-3.5" />
              <span>Qdrant Web UI</span>
              <ExternalLink className="w-3 h-3 ml-0.5" />
            </a>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center space-x-2 pt-6 border-t border-slate-800/80 mt-6">
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold font-mono transition flex items-center space-x-2 ${
              activeTab === 'recommendations'
                ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <CheckCircle className="w-3.5 h-3.5" />
            <span>Grounded Recommendations ({recommendations.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('documents')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold font-mono transition flex items-center space-x-2 ${
              activeTab === 'documents'
                ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Knowledge Documents ({documents.length || 7})</span>
          </button>

          <button
            onClick={() => setActiveTab('qdrant')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold font-mono transition flex items-center space-x-2 ${
              activeTab === 'qdrant'
                ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>Qdrant Vector Explorer</span>
          </button>
        </div>
      </div>

      {/* TAB 1: Grounded Recommendations */}
      {activeTab === 'recommendations' && (
        <div className="space-y-6">
          {recommendations.length === 0 ? (
            <div className="glass-panel rounded-2xl p-12 text-center text-slate-400">
              <BookOpen className="w-12 h-12 mx-auto mb-3 text-slate-600" />
              <p>No active project blueprint loaded. Run blueprint generation to see grounded recommendations.</p>
              <button
                onClick={() => setActiveTab('documents')}
                className="mt-4 text-xs font-mono text-brand-400 hover:underline"
              >
                Browse indexed knowledge documents &rarr;
              </button>
            </div>
          ) : (
            recommendations.map((rec, idx) => (
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

                <div className="text-sm text-slate-200 font-medium leading-relaxed bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  {rec.recommendation}
                </div>

                {rec.tradeoffs && (
                  <div className="text-xs text-slate-300 space-y-1">
                    <span className="font-semibold text-amber-400 font-mono">Architectural Trade-offs: </span>
                    <span>{rec.tradeoffs}</span>
                  </div>
                )}

                {rec.evidence && rec.evidence.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-slate-800">
                    <div className="text-xs font-bold text-slate-400 font-mono">Retrieved Knowledge Citations:</div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {rec.evidence.map((ev, evIdx) => (
                        <div key={evIdx} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                          <div className="flex items-center justify-between">
                            <span className="font-mono text-[11px] text-accent-cyan font-semibold">{ev.source_id}</span>
                            <span className="text-[10px] font-mono text-slate-500">Relevance: {ev.relevance_score}</span>
                          </div>
                          <div className="text-xs font-bold text-white">{ev.title}</div>
                          <div className="text-[11px] text-brand-300 font-mono">{ev.section}</div>
                          <p className="text-[11px] text-slate-300 leading-relaxed italic bg-black/40 p-2.5 rounded border border-slate-800">
                            "{ev.excerpt}"
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* TAB 2: Knowledge Documents Catalog */}
      {activeTab === 'documents' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                placeholder="Search documents, categories, or keywords..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-900/80 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500"
              />
            </div>
            <div className="text-xs font-mono text-slate-400">
              Showing {filteredDocs.length} of {documents.length} documents
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredDocs.map((doc) => (
              <div 
                key={doc.document_id} 
                className="glass-panel rounded-2xl p-5 space-y-3 border-t-2 border-t-brand-500 hover:border-slate-700 transition"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-accent-cyan px-2.5 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
                    {doc.document_id}
                  </span>
                  <span className="text-[11px] font-mono text-slate-400 bg-slate-800/60 px-2 py-0.5 rounded">
                    {doc.chunks_count} Hierarchical Chunks
                  </span>
                </div>

                <h3 className="font-display font-bold text-white text-base">{doc.title}</h3>

                <div className="text-xs text-slate-400 font-mono">
                  <span className="text-slate-500">Category: </span>
                  <span className="text-brand-300 font-medium">{doc.category}</span>
                </div>

                <div className="text-xs text-slate-300 bg-slate-900/70 p-3 rounded-xl border border-slate-800/80 space-y-1">
                  <div className="text-[11px] text-slate-400">
                    <strong className="text-slate-300 font-mono">Authoritative Source: </strong>
                    {doc.authoritative_source}
                  </div>
                  {doc.target_systems && (
                    <div className="text-[11px] text-slate-400">
                      <strong className="text-slate-300 font-mono">Target Systems: </strong>
                      {doc.target_systems}
                    </div>
                  )}
                </div>

                {/* Keywords Chips */}
                {doc.keywords && doc.keywords.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {doc.keywords.map((k) => (
                      <span key={k} className="text-[10px] font-mono text-slate-300 bg-slate-800/60 px-2 py-0.5 rounded border border-slate-700/60">
                        {k}
                      </span>
                    ))}
                  </div>
                )}

                {/* Subsections Overview */}
                {doc.sections && doc.sections.length > 0 && (
                  <div className="pt-2 border-t border-slate-800/80 text-xs">
                    <span className="text-[11px] font-mono text-slate-500 block mb-1.5">Indexed Sections:</span>
                    <ul className="text-[11px] text-slate-300 space-y-1 list-disc list-inside">
                      {doc.sections.slice(0, 4).map((s, idx) => (
                        <li key={idx} className="truncate">{s}</li>
                      ))}
                      {doc.sections.length > 4 && (
                        <li className="text-slate-500 font-mono">+{doc.sections.length - 4} more sections</li>
                      )}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: Qdrant Vector Engine Explorer */}
      {activeTab === 'qdrant' && (
        <div className="space-y-6">
          {/* Qdrant Status Card */}
          <div className="glass-panel rounded-2xl p-6 border-l-4 border-l-accent-cyan space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center space-x-2">
                <Database className="w-5 h-5 text-accent-cyan" />
                <h3 className="font-display font-bold text-white text-lg">Qdrant Vector Database Engine</h3>
              </div>
              <span className={`text-xs font-mono px-3 py-1 rounded-full border ${
                qdrantInfo?.qdrant_available 
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                  : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
              }`}>
                {qdrantInfo?.backend || 'Checking engine status...'}
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              Qdrant stores document vector points with HNSW (Hierarchical Navigable Small World) indexing for ultra-fast approximate nearest neighbor search and payload filtering.
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
              <div className="bg-slate-900/70 p-3 rounded-xl border border-slate-800">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Host Endpoint</div>
                <div className="text-xs font-mono text-slate-200 mt-0.5 truncate">{qdrantInfo?.qdrant_url || 'http://localhost:6333'}</div>
              </div>
              <div className="bg-slate-900/70 p-3 rounded-xl border border-slate-800">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Collection</div>
                <div className="text-xs font-mono text-brand-300 mt-0.5 truncate">{qdrantInfo?.collection_name || 'software_architecture_knowledge'}</div>
              </div>
              <div className="bg-slate-900/70 p-3 rounded-xl border border-slate-800">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Vector Dimension</div>
                <div className="text-xs font-mono text-slate-200 mt-0.5">{qdrantInfo?.vector_dimension || 384} (Cosine)</div>
              </div>
              <div className="bg-slate-900/70 p-3 rounded-xl border border-slate-800">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Indexed Chunks</div>
                <div className="text-xs font-mono text-emerald-400 mt-0.5">{chunks.length || qdrantInfo?.total_indexed_chunks || 0} Points</div>
              </div>
            </div>

            {/* How to view in Qdrant Box */}
            <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800 space-y-2">
              <div className="flex items-center space-x-2 text-xs font-bold text-white font-mono">
                <Compass className="w-4 h-4 text-brand-400" />
                <span>How to inspect your vectors & points in the Qdrant Dashboard:</span>
              </div>
              <ol className="text-xs text-slate-300 space-y-1.5 list-decimal list-inside leading-relaxed pl-1">
                <li>
                  Click the <strong className="text-brand-300">"Open Qdrant Web Dashboard"</strong> button below or navigate to{' '}
                  <a href="http://localhost:6333/dashboard" target="_blank" rel="noreferrer" className="text-accent-cyan underline">
                    http://localhost:6333/dashboard
                  </a>.
                </li>
                <li>
                  In the Qdrant left sidebar, click on <strong className="text-slate-200">"Collections"</strong> and select{' '}
                  <span className="font-mono text-brand-300 bg-slate-800 px-1.5 py-0.5 rounded text-[11px]">software_architecture_knowledge</span>.
                </li>
                <li>
                  Browse the table of stored points. Click any Point ID to inspect its 384-dimensional dense vector array and the rich JSON payload metadata (document ID, title, section hierarchy, breadcrumbs, keywords, and architectural text).
                </li>
              </ol>
              <div className="pt-2">
                <a
                  href="http://localhost:6333/dashboard"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-brand-500 hover:bg-brand-600 text-white text-xs font-mono font-bold transition shadow-lg shadow-brand-500/20"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>Launch Qdrant Web Dashboard (http://localhost:6333/dashboard)</span>
                </a>
              </div>
            </div>
          </div>

          {/* Searchable Chunks List */}
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center space-x-2 text-white font-display font-bold text-base">
                <FileText className="w-5 h-5 text-brand-400" />
                <h3>Hierarchical Vector Chunks Viewer</h3>
                <span className="text-xs font-mono text-slate-400">({filteredChunks.length})</span>
              </div>

              {/* Document Filter Dropdown */}
              <div className="flex items-center space-x-2">
                <select
                  value={selectedDocId || ''}
                  onChange={(e) => setSelectedDocId(e.target.value || null)}
                  className="bg-slate-900 border border-slate-800 rounded-lg text-xs font-mono text-slate-300 px-3 py-1.5 focus:outline-none focus:border-brand-500"
                >
                  <option value="">All Documents</option>
                  {documents.map((d) => (
                    <option key={d.document_id} value={d.document_id}>
                      {d.document_id} — {d.title}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-3">
              {filteredChunks.map((chunk) => (
                <div key={chunk.id} className="glass-panel rounded-xl p-4 space-y-2 border-l-2 border-l-brand-400/80">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-[11px] font-bold text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded border border-brand-500/20">
                        {chunk.id}
                      </span>
                      <span className="font-display font-bold text-white text-xs">{chunk.title}</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500">{chunk.character_count} chars</span>
                  </div>

                  <div className="text-[11px] font-mono text-accent-cyan bg-slate-900/80 px-2.5 py-1 rounded border border-slate-800 truncate">
                    {chunk.breadcrumb}
                  </div>

                  <p className="text-xs text-slate-300 bg-slate-900/60 p-3 rounded-lg border border-slate-800/80 font-mono leading-relaxed">
                    {chunk.excerpt}
                  </p>

                  {chunk.keywords && chunk.keywords.length > 0 && (
                    <div className="flex flex-wrap gap-1 pt-1">
                      {chunk.keywords.map((k) => (
                        <span key={k} className="text-[9px] font-mono text-slate-400 bg-slate-800/70 px-1.5 py-0.5 rounded">
                          {k}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
