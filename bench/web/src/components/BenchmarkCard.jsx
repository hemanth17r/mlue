import React, { useState } from 'react';
import { 
  Layers, 
  Sparkles, 
  Compass, 
  Activity, 
  ShieldCheck, 
  Zap, 
  Database, 
  GitBranch, 
  Lock, 
  ShieldAlert,
  ChevronDown, 
  ChevronUp, 
  CheckCircle2, 
  AlertCircle,
  HelpCircle,
  Code2,
  CheckCircle
} from 'lucide-react';

export default function BenchmarkCard({ benchmark }) {
  const [expanded, setExpanded] = useState(false);

  const getIcon = (id) => {
    switch (id) {
      case 'B1': return <Layers className="w-4 h-4 text-cyan-400" />;
      case 'B2': return <Sparkles className="w-4 h-4 text-sand-400" />;
      case 'B3': return <Compass className="w-4 h-4 text-cyan-300" />;
      case 'B4': return <Activity className="w-4 h-4 text-emerald-400" />;
      case 'B5': return <ShieldCheck className="w-4 h-4 text-indigo-400" />;
      case 'B6': return <Zap className="w-4 h-4 text-amber-400" />;
      case 'B7': return <Database className="w-4 h-4 text-teal-400" />;
      case 'B8': return <GitBranch className="w-4 h-4 text-purple-400" />;
      case 'B9': return <Lock className="w-4 h-4 text-emerald-300" />;
      case 'B10': return <ShieldAlert className="w-4 h-4 text-rose-400" />;
      default: return <Activity className="w-4 h-4 text-cyan-400" />;
    }
  };

  const renderGauge = () => {
    switch (benchmark.format_type) {
      case 'tier_and_count':
        const tiers = ['L0', 'L1', 'L2', 'L3', 'L4'];
        return (
          <div className="space-y-2.5">
            <div className="flex items-baseline justify-between font-mono">
              <span className="text-xl font-bold text-cyan-300 tracking-tight">{benchmark.tier}</span>
              <span className="text-xs text-emerald-400 font-semibold">{benchmark.import_violations} Violations</span>
            </div>
            <div className="grid grid-cols-5 gap-1 pt-0.5">
              {tiers.map((t, idx) => (
                <div 
                  key={idx} 
                  className={`text-center py-1 rounded text-[10px] font-mono border transition-all ${
                    idx === 1 
                      ? 'bg-cyan-500/20 border-cyan-400 text-cyan-200 font-bold shadow-[0_0_10px_rgba(6,182,212,0.3)]' 
                      : idx < 1 
                      ? 'bg-emerald-950/40 border-emerald-800/30 text-emerald-300' 
                      : 'bg-black/40 border-white/[0.04] text-slate-600'
                  }`}
                >
                  {t}
                </div>
              ))}
            </div>
          </div>
        );

      case 'multiplier':
        return (
          <div className="space-y-2 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-sand-400 tracking-tight">{benchmark.multiplier}</span>
              <span className="text-xs text-emerald-400 font-semibold">{benchmark.heuristic_violations} Heuristics</span>
            </div>
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-amber-500 to-yellow-400 rounded-full shadow-[0_0_8px_rgba(245,158,11,0.5)]" style={{ width: '70%' }} />
            </div>
          </div>
        );

      case 'log_precision':
        return (
          <div className="space-y-2 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-cyan-300 tracking-tight">{benchmark.log_precision_decades}</span>
              <span className="text-xs text-emerald-400 font-semibold">Δ = {benchmark.raw_drift.toFixed(1)}</span>
            </div>
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-cyan-500 to-teal-300 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.5)]" style={{ width: '100%' }} />
            </div>
          </div>
        );

      case 'ppb_drift':
        return (
          <div className="space-y-2 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-emerald-400 tracking-tight">{benchmark.drift_ppb}</span>
              <span className="text-xs text-emerald-400 font-semibold">&lt; 1,000 PPB</span>
            </div>
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-emerald-400 rounded-full shadow-[0_0_8px_rgba(52,211,153,0.5)]" style={{ width: '100%' }} />
            </div>
          </div>
        );

      case 'fraction_gate':
        return (
          <div className="space-y-2 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-indigo-300 tracking-tight">{benchmark.blocked_cases}</span>
              <span className="text-xs text-emerald-400 font-semibold">{benchmark.rejection_rate} Blocked</span>
            </div>
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 rounded-full shadow-[0_0_8px_rgba(99,102,241,0.5)]" style={{ width: '100%' }} />
            </div>
          </div>
        );

      case 'speed_and_latency':
        return (
          <div className="space-y-2 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-amber-400 tracking-tight">{benchmark.ticks_per_sec}</span>
              <span className="text-xs text-slate-300 font-semibold">{benchmark.latency_us}</span>
            </div>
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-amber-500 to-yellow-400 rounded-full shadow-[0_0_8px_rgba(245,158,11,0.5)]" style={{ width: '85%' }} />
            </div>
          </div>
        );

      case 'memory_churn':
        return (
          <div className="space-y-2 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-teal-300 tracking-tight">{benchmark.bytes_per_step}</span>
              <span className="text-xs text-emerald-400 font-semibold">{benchmark.total_churn_kb} Churn</span>
            </div>
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-teal-400 rounded-full shadow-[0_0_8px_rgba(45,212,191,0.5)]" style={{ width: '15%' }} />
            </div>
          </div>
        );

      case 'cyclomatic_score':
        return (
          <div className="space-y-2 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-purple-300 tracking-tight">CC = {benchmark.max_cyclomatic_score}</span>
              <span className="text-xs text-emerald-400 font-semibold">Bounded</span>
            </div>
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-purple-500 to-indigo-400 rounded-full shadow-[0_0_8px_rgba(168,85,247,0.5)]" 
                style={{ width: `${Math.min(100, (benchmark.max_cyclomatic_score / 30) * 100)}%` }} 
              />
            </div>
          </div>
        );

      case 'cryptographic_hash':
        return (
          <div className="space-y-2 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-base font-bold text-emerald-300 tracking-tight">BIT-EXACT 50K</span>
              <span className="text-xs text-emerald-400 font-semibold">100% Match</span>
            </div>
            <div className="bg-black/50 px-2.5 py-1 rounded border border-emerald-500/20 text-[10px] font-mono text-emerald-400/90 truncate">
              {benchmark.full_hash}
            </div>
          </div>
        );

      case 'containment_speed':
        return (
          <div className="space-y-2 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-rose-300 tracking-tight">{benchmark.max_containment_speed}</span>
              <span className="text-xs text-emerald-400 font-semibold">{benchmark.defect_rate}</span>
            </div>
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-rose-500 to-pink-400 rounded-full shadow-[0_0_8px_rgba(244,63,94,0.5)]" style={{ width: '100%' }} />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const exp = benchmark.explanation || {};

  return (
    <div className="p-5 rounded-2xl apple-glass flex flex-col justify-between transition-all duration-300 group">
      
      <div>
        {/* Card Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-black/40 border border-white/[0.06] group-hover:border-cyan-500/30 transition-colors">
              {getIcon(benchmark.id)}
            </div>
            <div>
              <div className="flex items-center space-x-1.5 font-mono">
                <span className="text-[10px] font-bold text-cyan-400 px-1.5 py-0.2 rounded bg-cyan-950/60 border border-cyan-800/40">
                  {benchmark.id}
                </span>
                <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">
                  {benchmark.category}
                </span>
              </div>
              <h3 className="text-sm font-semibold text-white tracking-tight mt-0.5 font-mono">
                {benchmark.name}
              </h3>
            </div>
          </div>

          <div className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold flex items-center space-x-1 border ${
            benchmark.passed 
              ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300' 
              : 'bg-rose-950/40 border-rose-500/30 text-rose-300'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${benchmark.passed ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.8)]' : 'bg-rose-400'}`} />
            <span>{benchmark.passed ? 'PASS' : 'FAIL'}</span>
          </div>
        </div>

        {/* Target Standard */}
        <div className="text-[11px] font-mono text-slate-400 mb-3 bg-black/30 px-2.5 py-1 rounded-lg border border-white/[0.04] flex justify-between">
          <span className="text-slate-500">Standard:</span>
          <span className="text-slate-300 font-medium">{benchmark.target}</span>
        </div>

        {/* Primary Multi-Format Display */}
        <div className="py-1">
          {renderGauge()}
        </div>
      </div>

      {/* Dynamic How It Works & Measurement Drawer */}
      <div className="border-t border-white/[0.04] pt-2.5 mt-3">
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-between text-[11px] text-slate-400 hover:text-cyan-300 transition-colors font-mono"
        >
          <span className="flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5 text-cyan-400" />
            <span>How It Works & Measurement</span>
          </span>
          {expanded ? <ChevronUp className="w-3.5 h-3.5 text-cyan-400" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {expanded && (
          <div className="mt-3 space-y-2.5 text-[11px] font-mono text-slate-300 bg-black/60 p-3.5 rounded-xl border border-white/[0.06] shadow-inner">
            
            {/* 1. What It Tests */}
            {exp.what_it_tests && (
              <div>
                <span className="text-cyan-400 font-semibold block text-[10px] uppercase tracking-wider mb-0.5">🎯 What It Tests</span>
                <p className="text-slate-300 text-[11px] leading-relaxed">{exp.what_it_tests}</p>
              </div>
            )}

            {/* 2. What We Measure */}
            {exp.what_we_measure && (
              <div>
                <span className="text-sand-400 font-semibold block text-[10px] uppercase tracking-wider mb-0.5">📏 What We Measure</span>
                <p className="text-slate-300 text-[11px] leading-relaxed">{exp.what_we_measure}</p>
              </div>
            )}

            {/* 3. How It's Measured */}
            {exp.how_its_measured && (
              <div>
                <span className="text-emerald-400 font-semibold block text-[10px] uppercase tracking-wider mb-0.5">⚙️ How It's Measured</span>
                <p className="text-slate-300 text-[11px] leading-relaxed">{exp.how_its_measured}</p>
              </div>
            )}

            {/* 4. How To Compare */}
            {exp.how_to_compare && (
              <div>
                <span className="text-indigo-400 font-semibold block text-[10px] uppercase tracking-wider mb-0.5">📊 How To Compare</span>
                <p className="text-slate-300 text-[11px] leading-relaxed">{exp.how_to_compare}</p>
              </div>
            )}

            {/* 5. Formula Chip */}
            {benchmark.formula && (
              <div className="pt-1 border-t border-white/[0.06]">
                <span className="text-slate-500 font-semibold block text-[10px] uppercase tracking-wider mb-1">🔬 Invariant Formula</span>
                <code className="text-cyan-300 text-[10px] block bg-black/80 p-2 rounded border border-cyan-500/20">
                  {benchmark.formula}
                </code>
              </div>
            )}

          </div>
        )}
      </div>

    </div>
  );
}
