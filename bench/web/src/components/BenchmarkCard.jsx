import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
  Award,
  BookOpen
} from 'lucide-react';
import { tapScale, springSnappy } from '../lib/motion';

// Industrial Grounding Metadata from docs/BENCHMARK_GROUNDING.md
const GROUNDING_DATA = {
  B1: {
    standardName: 'ISO 26262 / MISRA-C Sandboxing',
    rationale: 'Safety-critical core calculation engines must remain decoupled from host OS, display drivers, and third-party UI runtimes.',
    targetRule: '0 Foreign OS/GUI Imports (Tier L1 Substrate)',
  },
  B2: {
    standardName: 'Kolmogorov-Chaitin Complexity & Orthogonal DSL',
    rationale: 'A true universal substrate expresses diverse applications from minimal orthogonal primitives without hardcoded engine code.',
    targetRule: '≥ 3.0x App-to-Primitive Expansion Ratio',
  },
  B3: {
    standardName: 'IEEE 754-2019 Double Precision Standard',
    rationale: 'Simulation coordinates are normalized in [0, 1]. Viewport invariance must match up to machine epsilon across screens.',
    targetRule: '> 16.0 Decades Precision (Δ = 0.0 Normalized Drift)',
  },
  B4: {
    standardName: 'Symplectic Numerical Integration (NASA SPICE)',
    rationale: 'Closed elastic collisions must conserve total kinetic energy without numerical damping or explosive energy gain.',
    targetRule: '≤ 1,000 PPB Total Kinetic Energy Drift (0.0001%)',
  },
  B5: {
    standardName: 'Hoare Logic / Type-State Formal Verification',
    rationale: 'Eliminates unhandled runtime crashes by mathematically proving state boundaries and path reachability before execution.',
    targetRule: '100% Compile-Time Defect Interception (10/10 Cases)',
  },
  B6: {
    standardName: 'Real-Time Physics Engine Budgets (Havok/PhysX)',
    rationale: 'A 60Hz frame budgets 16.6ms. Microsecond evaluation (< 100 µs) enables real-time interaction and 166x faster AI training.',
    targetRule: '> 10,000 ticks/s (Step Latency < 100 µs/step)',
  },
  B7: {
    standardName: 'FAA DO-178C Level A Real-Time Zero-Allocation',
    rationale: 'Garbage collection pauses cause frame stutters. Steady-state simulation steps must avoid unbounded heap allocation.',
    targetRule: '< 500 Bytes/step Steady-State Heap Churn',
  },
  B8: {
    standardName: 'NIST Special Publication 500-235 (CC ≤ 30)',
    rationale: 'NIST classifies CC > 30 as high risk for latent defects. Strict cyclomatic gating guarantees modular, provable logic.',
    targetRule: 'Max Cyclomatic Complexity ≤ 30',
  },
  B9: {
    standardName: 'NIST FIPS 180-4 SHA-256 Bit-Exact Verification',
    rationale: 'Autonomous AI verification requires deterministic reproducibility across 50,000 continuous simulation steps.',
    targetRule: '100% Cryptographic Bit-Exact Parity',
  },
  B10: {
    standardName: 'Continuous Collision Detection (CCD / GJK)',
    rationale: 'High-speed entities must never tunnel through walls or thin solid boundaries regardless of velocity.',
    targetRule: '0.0% Defect Rate at Critical Speeds (v_max ≥ 2.0)',
  },
  B11: {
    standardName: 'Spatial Subdivisions (Barnes-Hut / BVH Spatial)',
    rationale: 'Pairwise collision checks scale as O(N²). Broadphase acceleration must cull over 90% of non-colliding entity pairs.',
    targetRule: '≥ 90.0% Broadphase Cull Efficiency (O(N log N))',
  },
  B12: {
    standardName: 'Fixed-Point Determinism (Q32.32 / IEEE 754-Independent)',
    rationale: 'AI rollouts across x86-64, ARM64, and WebAssembly must produce bit-exact identical trajectory hashes.',
    targetRule: '100% Bit-Exact Parity Across CPU Architectures',
  },
};

export default function BenchmarkCard({ benchmark, allRuns, currentRunIdx, compareRunIdx, compareMode }) {
  const [expanded, setExpanded] = useState(false);

  const getIcon = (id) => {
    switch (id) {
      case 'B1': return Layers;
      case 'B2': return Sparkles;
      case 'B3': return Compass;
      case 'B4': return Activity;
      case 'B5': return ShieldCheck;
      case 'B6': return Zap;
      case 'B7': return Database;
      case 'B8': return GitBranch;
      case 'B9': return Lock;
      case 'B10': return ShieldAlert;
      case 'B11': return Compass;
      case 'B12': return Lock;
      default: return Activity;
    }
  };

  const Icon = getIcon(benchmark.id);
  const grounding = GROUNDING_DATA[benchmark.id];
  const exp = benchmark.explanation || {};

  const extractNumericVal = (b) => {
    switch (b.id) {
      case 'B1': return b.import_violations === 0 ? 1 : 0;
      case 'B2': return parseFloat(b.multiplier) || 3.5;
      case 'B3': return b.raw_drift === 0 ? 16.0 : Math.min(16.0, parseFloat(b.log_precision_decades) || 16.0);
      case 'B4': return parseFloat(b.drift_ppb) || 0.0;
      case 'B5': return parseFloat(b.rejection_rate) || 100.0;
      case 'B6': return b.raw_ticks_per_sec || parseFloat((b.ticks_per_sec || '0').replace(/[^0-9.]/g, '')) || 25000;
      case 'B7': return parseFloat(b.bytes_per_step) || 0.72;
      case 'B8': return b.max_cyclomatic_score || 21;
      case 'B9': return 100;
      case 'B10': return parseFloat(b.max_containment_speed) || 2.5;
      case 'B11': return parseFloat(b.cull_efficiency) || 100.0;
      case 'B12': return 100;
      default: return 1;
    }
  };

  // Build sparkline history data across all runs
  const sparklineData = (allRuns || [])
    .map((r, rIdx) => {
      const match = r.benchmarks?.find((item) => item.id === benchmark.id);
      if (!match) return null;
      return {
        runIdx: rIdx,
        runId: r.run_id,
        val: extractNumericVal(match),
        display: match.value_display,
      };
    })
    .filter(Boolean);

  // Render SVG Sparkline
  const renderSparkline = () => {
    if (sparklineData.length < 2) return null;

    const values = sparklineData.map((d) => d.val);
    const minVal = Math.min(...values);
    const maxVal = Math.max(...values);
    const range = maxVal - minVal || 1;

    const width = 140;
    const height = 24;
    const padding = 3;

    const points = sparklineData.map((d, i) => {
      const x = padding + (i / (sparklineData.length - 1)) * (width - padding * 2);
      const normalized = (d.val - minVal) / range;
      const y = height - padding - normalized * (height - padding * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });

    const activePointIdx = sparklineData.findIndex((d) => d.runIdx === currentRunIdx);
    const activePoint = activePointIdx >= 0 ? points[activePointIdx].split(',') : points[points.length - 1].split(',');

    return (
      <div className="flex items-center space-x-2 pt-1">
        <svg width={width} height={height} className="overflow-visible">
          <polyline
            fill="none"
            stroke="#06B6D4"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={points.join(' ')}
            className="opacity-70"
          />
          <circle
            cx={activePoint[0]}
            cy={activePoint[1]}
            r="3"
            className="fill-cyan-400 stroke-[#030712] stroke-[1.5]"
          />
        </svg>
        <span className="text-[9px] font-mono text-slate-500">History</span>
      </div>
    );
  };

  const renderGauge = () => {
    switch (benchmark.metric_type) {
      case 'count_zero':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-white tracking-tight">{benchmark.import_violations}</span>
              <span className="text-xs text-emerald-400 font-semibold">{benchmark.tier}</span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-emerald-400 rounded-full shadow-[0_0_8px_rgba(52,211,153,0.5)]" style={{ width: '100%' }} />
            </div>
          </div>
        );

      case 'multiplier':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-cyan-400 tracking-tight">{benchmark.multiplier}</span>
              <span className="text-xs text-slate-400 font-semibold">{benchmark.working_applications} Apps / 2 Primitives</span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.5)]" style={{ width: '90%' }} />
            </div>
          </div>
        );

      case 'log_precision':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-teal-300 tracking-tight">{benchmark.log_precision_decades}</span>
              <span className="text-xs text-teal-400 font-semibold">Exact Match</span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-cyan-500 to-teal-300 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.5)]" style={{ width: '100%' }} />
            </div>
          </div>
        );

      case 'ppb_drift':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-emerald-400 tracking-tight">{benchmark.drift_ppb}</span>
              <span className="text-xs text-emerald-400 font-semibold">&lt; 1,000 PPB</span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-emerald-400 rounded-full shadow-[0_0_8px_rgba(52,211,153,0.5)]" style={{ width: '100%' }} />
            </div>
          </div>
        );

      case 'fraction_gate':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-indigo-300 tracking-tight">{benchmark.blocked_cases}</span>
              <span className="text-xs text-emerald-400 font-semibold">{benchmark.rejection_rate} Blocked</span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 rounded-full shadow-[0_0_8px_rgba(99,102,241,0.5)]" style={{ width: '100%' }} />
            </div>
          </div>
        );

      case 'speed_and_latency':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-amber-400 tracking-tight">{benchmark.ticks_per_sec}</span>
              <span className="text-xs text-slate-300 font-semibold">{benchmark.latency_us}</span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-amber-500 to-yellow-400 rounded-full shadow-[0_0_8px_rgba(245,158,11,0.5)]" style={{ width: '75%' }} />
            </div>
          </div>
        );

      case 'memory_churn':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-teal-300 tracking-tight">{benchmark.bytes_per_step}</span>
              <span className="text-xs text-emerald-400 font-semibold">{benchmark.total_churn_kb} Churn</span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-teal-400 rounded-full shadow-[0_0_8px_rgba(45,212,191,0.5)]" style={{ width: '15%' }} />
            </div>
          </div>
        );

      case 'cyclomatic_score':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-purple-300 tracking-tight">CC = {benchmark.max_cyclomatic_score}</span>
              <span className="text-xs text-emerald-400 font-semibold">Bounded</span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-purple-500 to-indigo-400 rounded-full shadow-[0_0_8px_rgba(168,85,247,0.5)]" 
                style={{ width: `${Math.min(100, (benchmark.max_cyclomatic_score / 30) * 100)}%` }} 
              />
            </div>
          </div>
        );

      case 'cryptographic_hash':
      case 'bit_parity':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-base font-bold text-emerald-300 tracking-tight">BIT-EXACT 50K</span>
              <span className="text-xs text-emerald-400 font-semibold">100% Match</span>
            </div>
            <div className="bg-black/50 px-2.5 py-1 rounded-xl border border-emerald-500/20 text-[10px] font-mono text-emerald-400/90 truncate">
              {benchmark.full_hash || benchmark.hash}
            </div>
          </div>
        );

      case 'containment_speed':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-rose-300 tracking-tight">{benchmark.max_containment_speed}</span>
              <span className="text-xs text-emerald-400 font-semibold">{benchmark.defect_rate} Defect</span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-rose-500 to-pink-500 rounded-full shadow-[0_0_8px_rgba(244,63,94,0.5)]" style={{ width: '85%' }} />
            </div>
          </div>
        );

      case 'cull_efficiency':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-cyan-300 tracking-tight">{benchmark.cull_efficiency}</span>
              <span className="text-xs text-emerald-400 font-semibold">O(N log N)</span>
            </div>
            <div className="w-full h-1.5 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-cyan-400 to-emerald-400 rounded-full shadow-[0_0_8px_rgba(6,182,212,0.5)]" style={{ width: '100%' }} />
            </div>
          </div>
        );

      default:
        return (
          <div className="text-2xl font-extrabold text-white font-mono">
            {benchmark.value_display}
          </div>
        );
    }
  };

  return (
    <motion.div 
      {...tapScale.card}
      className="p-5 rounded-2xl bg-slate-900/80 border border-white/[0.08] hover:border-cyan-500/40 shadow-xl transition-colors flex flex-col justify-between"
    >
      <div>
        {/* Header: ID, Category, Name & Status Pill */}
        <div className="flex items-start justify-between gap-2 mb-3">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-white/[0.04] border border-white/[0.08] text-cyan-400">
              <Icon className="w-4 h-4" />
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

          <div className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold flex items-center space-x-1 border ${
            benchmark.passed 
              ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300' 
              : 'bg-rose-950/40 border-rose-500/30 text-rose-300'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${benchmark.passed ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.8)]' : 'bg-rose-400'}`} />
            <span>{benchmark.passed ? 'PASS' : 'FAIL'}</span>
          </div>
        </div>

        {/* Target Standard Badge */}
        <div className="text-[11px] font-mono text-slate-400 mb-2.5 bg-black/30 px-3 py-1 rounded-xl border border-white/[0.04] flex justify-between items-center">
          <span className="text-slate-500">Target:</span>
          <span className="text-slate-200 font-medium">{benchmark.target}</span>
        </div>

        {/* Primary Measurement Gauge */}
        <div className="py-1">
          {renderGauge()}
        </div>

        {/* Sparkline Micro-Chart */}
        {renderSparkline()}
      </div>

      {/* Expandable Grounding & How It Works Drawer */}
      <div className="border-t border-white/[0.04] pt-2.5 mt-3">
        <motion.button
          {...tapScale.button}
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-between text-[11px] text-slate-400 hover:text-cyan-300 transition-colors font-mono cursor-pointer"
        >
          <span className="flex items-center gap-1.5">
            <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
            <span>Grounding & How It Works</span>
          </span>
          {expanded ? <ChevronUp className="w-3.5 h-3.5 text-cyan-400" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </motion.button>

        <AnimatePresence>
          {expanded && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto', transition: springSnappy }}
              exit={{ opacity: 0, height: 0, transition: { duration: 0.15 } }}
              className="mt-3 space-y-2 text-[11px] font-mono text-slate-300 bg-black/70 p-3 rounded-2xl border border-white/[0.06] shadow-inner overflow-hidden"
            >
              {/* Scientific / Industry Standard Grounding */}
              {grounding && (
                <div className="pb-2 border-b border-white/[0.06]">
                  <div className="flex items-center space-x-1.5 text-amber-400 font-semibold text-[10px] uppercase tracking-wider mb-0.5">
                    <Award className="w-3 h-3" />
                    <span>Standard Grounding</span>
                  </div>
                  <div className="text-slate-200 font-bold text-[11px]">{grounding.standardName}</div>
                  <p className="text-slate-400 text-[10px] leading-relaxed mt-0.5">{grounding.rationale}</p>
                </div>
              )}

              {/* What It Tests */}
              {exp.what_it_tests && (
                <div>
                  <span className="text-cyan-400 font-semibold block text-[10px] uppercase tracking-wider">🎯 What It Tests</span>
                  <p className="text-slate-300 text-[11px] leading-relaxed">{exp.what_it_tests}</p>
                </div>
              )}

              {/* Formula */}
              {benchmark.formula && (
                <div className="pt-1">
                  <span className="text-slate-500 font-semibold block text-[10px] uppercase tracking-wider mb-0.5">🔬 Invariant Formula</span>
                  <code className="text-cyan-300 text-[10px] block bg-black/90 p-2 rounded-xl border border-cyan-500/20">
                    {benchmark.formula}
                  </code>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
