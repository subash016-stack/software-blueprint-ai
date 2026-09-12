import React, { useState, useEffect } from 'react';
import { X, Activity, Zap, HardDrive, Clock, ShieldCheck, RefreshCw } from 'lucide-react';
import { getMetrics } from '../services/api';

export default function MetricsModal({ isOpen, onClose }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const data = await getMetrics();
      setMetrics(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchMetrics();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-[#111827] border border-slate-700 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-accent-cyan" />
            <h3 className="font-display font-bold text-white text-base">Observability & Token Metrics</h3>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={fetchMetrics}
              disabled={loading}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
              title="Refresh metrics"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="flex items-center space-x-2 text-slate-400 text-xs mb-1">
                <Zap className="w-4 h-4 text-amber-400" />
                <span>Total LLM Calls</span>
              </div>
              <div className="text-2xl font-bold font-mono text-white">{metrics?.total_llm_calls || 0}</div>
            </div>

            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="flex items-center space-x-2 text-slate-400 text-xs mb-1">
                <HardDrive className="w-4 h-4 text-emerald-400" />
                <span>Cache Hits</span>
              </div>
              <div className="text-2xl font-bold font-mono text-emerald-400">{metrics?.cache_hits || 0}</div>
            </div>

            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="flex items-center space-x-2 text-slate-400 text-xs mb-1">
                <ShieldCheck className="w-4 h-4 text-brand-400" />
                <span>Cache Hit Rate</span>
              </div>
              <div className="text-2xl font-bold font-mono text-brand-400">
                {metrics?.cache_hit_rate_percent || 0}%
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="flex items-center space-x-2 text-slate-400 text-xs mb-1">
                <Clock className="w-4 h-4 text-accent-cyan" />
                <span>Avg LLM Latency</span>
              </div>
              <div className="text-2xl font-bold font-mono text-accent-cyan">
                {metrics?.average_llm_latency_ms || 0} <span className="text-xs text-slate-400">ms</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="flex items-center space-x-2 text-slate-400 text-xs mb-1">
                <Zap className="w-4 h-4 text-purple-400" />
                <span>Est. Input Tokens</span>
              </div>
              <div className="text-2xl font-bold font-mono text-purple-400">
                {metrics?.estimated_input_tokens || 0}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
              <div className="flex items-center space-x-2 text-slate-400 text-xs mb-1">
                <Sparkles className="w-4 h-4 text-rose-400" />
                <span>Est. Tokens Saved</span>
              </div>
              <div className="text-2xl font-bold font-mono text-rose-400">
                {metrics?.estimated_tokens_saved || 0}
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 font-mono text-xs text-slate-300 space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-500">Hardware Profile:</span>
              <span className="text-slate-300">Intel i5-12450H • 16GB RAM • RTX 2050 4GB</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Primary Model:</span>
              <span className="text-slate-300">qwen3:4b (Local Ollama)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Embedding Engine:</span>
              <span className="text-slate-300">qwen3-embedding:0.6b (Qdrant Vector Store)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Cache Layer:</span>
              <span className="text-slate-300">Redis / Resilient In-Memory LRU</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Sparkles(props) {
  return (
    <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
    </svg>
  );
}
