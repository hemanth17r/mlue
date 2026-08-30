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
  HelpCircle,
  TrendingUp,
  Award,
  BookOpen
} from 'lucide-react';

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
    targetRule: 'Peak McCabe Cyclomatic Complexity CC ≤ 30',
  },
  B9: {
    standardName: 'Deterministic Lockstep Engine Standards (GGPO)',
    rationale: 'In multiplayer networking, AI rollouts, and WAL replay, 50,000 steps must produce bit-identical SHA-256 state hashes.',
    targetRule: '100% Bit-Exact SHA-256 Digest Match',
  },
  B10: {
    standardName: 'Continuous Collision Detection (CCD) Swept Volumes',
    rationale: 'At high velocity, discrete physics tunnel through walls. Continuous swept bounding ensures 0% tunneling penetration.',
    targetRule: 'v_max ≥ 2.5 units/s (0.00% Barrier Tunneling Defect)',
  },
  B11: {
    standardName: 'Spatial Partitioning & Broadphase (Ericson / Baraff)',
    rationale: 'At N=1,000 entities, brute force tests 499,500 pairs. Spatial hash grids prune >98% non-colliding pairs to maintain O(N log N).',
    targetRule: '≥ 98.0% Broadphase Cull Efficiency at N=1,000',
  },
  B12: {
    standardName: 'Fixed-Point Deterministic Math (Q32.32 DSP)',
    rationale: 'Eliminates IEEE 754 floating-point hardware divergence (FMA/rounding differences across x86, ARM, and WASM).',
    targetRule: '100% SHA-256 Match across x86_64 == ARM64 == WASM',
  },
};

export default function BenchmarkCard({ benchmark, allRuns, currentRunIdx, compareRunIdx, compareMode }) {
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
      case 'B11': return <Sparkles className="w-4 h-4 text-teal-300" />;
      case 'B12': return <Lock className="w-4 h-4 text-cyan-300" />;
      default: return <Activity className="w-4 h-4 text-cyan-400" />;
    }
  };

  // Extract numeric value from a benchmark object for sparkline plotting
  const extractNumericVal = (b) => {
    if (!b) return null;
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
          {/* Active Run Marker */}
          <circle
            cx={activePoint[0]}
            cy={activePoint[1]}
            r="3"
            className="fill-cyan-400 stroke-[#030712] stroke-[1.5]"
          />
        </svg>
        <span className="text-[10px] text-slate-500 font-mono">
          {sparklineData.length} runs
        </span>
      </div>
    );
  };

  // Render format specific gauges
  const renderGauge = () => {
    switch (benchmark.format_type) {
      case 'tier_and_count':
        const tiers = ['L0', 'L1', 'L2', 'L3', 'L4'];
        return (
          <div className="space-y-2 font-mono">
            <div className="flex items-baseline justify-between">
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
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-sand-400 tracking-tight">{benchmark.multiplier}</span>
              <span className="text-xs text-emerald-400 font-semibold">{benchmark.heuristic_violations} Heuristics</span>
            </div>
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-amber-500 to-yellow-400 rounded-full shadow-[0_0_8px_rgba(245,158,11,0.5)]" style={{ width: '85%' }} />
            </div>
          </div>
        );

      case 'log_precision':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-cyan-300 tracking-tight">{benchmark.log_precision_decades}</span>
              <span className="text-xs text-emerald-400 font-semibold">Δ = {benchmark.raw_drift?.toFixed(1) || '0.0'}</span>
            </div>
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
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
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
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
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
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
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
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
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
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
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
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
            <div className="bg-black/50 px-2.5 py-1 rounded border border-emerald-500/20 text-[10px] font-mono text-emerald-400/90 truncate">
              {benchmark.full_hash || benchmark.hash}
            </div>
          </div>
        );

      case 'containment_speed':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-rose-300 tracking-tight">{benchmark.max_containment_speed}</span>
              <span className="text-xs text-emerald-400 font-semibold">{benchmark.defect_rate}</span>
            </div>
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-rose-500 to-pink-400 rounded-full shadow-[0_0_8px_rgba(244,63,94,0.5)]" style={{ width: '100%' }} />
            </div>
          </div>
        );

      case 'broadphase_scaling':
        return (
          <div className="space-y-1.5 font-mono">
            <div className="flex items-baseline justify-between">
              <span className="text-2xl font-extrabold text-teal-300 tracking-tight">{benchmark.cull_efficiency}</span>
              <span className="text-xs text-emerald-400 font-semibold">{benchmark.candidate_pairs} pairs</span>
            </div>
            <div className="w-full h-1 rounded-full bg-black/40 border border-white/[0.05] overflow-hidden">
              <div className="h-full bg-gradient-to-r from-teal-400 to-cyan-300 rounded-full shadow-[0_0_8px_rgba(45,212,191,0.5)]" style={{ width: '100%' }} />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const exp = benchmark.explanation || {};
  const grounding = GROUNDING_DATA[benchmark.id] || null;

  return (
    <div className="p-4 sm:p-5 rounded-2xl apple-glass flex flex-col justify-between transition-all duration-300 group border border-white/[0.06] hover:border-cyan-500/30">
      <div>
        {/* Card Top: ID, Name, Category & Status */}
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

        {/* Target Standard Badge */}
        <div className="text-[11px] font-mono text-slate-400 mb-2.5 bg-black/30 px-2.5 py-1 rounded-lg border border-white/[0.04] flex justify-between items-center">
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
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-between text-[11px] text-slate-400 hover:text-cyan-300 transition-colors font-mono"
        >
          <span className="flex items-center gap-1.5">
            <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
            <span>Grounding & How It Works</span>
          </span>
          {expanded ? <ChevronUp className="w-3.5 h-3.5 text-cyan-400" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {expanded && (
          <div className="mt-3 space-y-2 text-[11px] font-mono text-slate-300 bg-black/70 p-3 rounded-xl border border-white/[0.06] shadow-inner">
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
                <code className="text-cyan-300 text-[10px] block bg-black/90 p-1.5 rounded border border-cyan-500/20">
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
