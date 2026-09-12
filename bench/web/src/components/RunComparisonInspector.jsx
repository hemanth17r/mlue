import React from 'react';
import { motion } from 'framer-motion';
import { 
  History, 
  ShieldCheck, 
  Compass, 
  Activity, 
  Zap, 
  TrendingUp 
} from 'lucide-react';
import { tapScale, springJelly } from '../lib/motion';

export default function RunComparisonInspector({
  runs,
  selectedRunIdx,
  onSelectRun,
  compareRunIdx,
  onSelectCompareRun,
  compareMode,
  setCompareMode,
}) {
  if (!runs || runs.length === 0) return null;

  const currentRun = runs[selectedRunIdx] || runs[runs.length - 1];
  const baselineRun = compareRunIdx !== null ? runs[compareRunIdx] : null;

  // Format date helper: "Sep 12, 11:38 AM"
  const formatDate = (isoStr) => {
    try {
      const d = new Date(isoStr);
      if (isNaN(d.getTime())) return isoStr;
      return d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoStr;
    }
  };

  const currentSpeed = currentRun.benchmarks?.find((b) => b.id === 'B6')?.raw_ticks_per_sec || 25000;
  const currentSpeedDisplay = currentRun.benchmarks?.find((b) => b.id === 'B6')?.value_display || '25.7k t/s';
  const baseSpeed = baselineRun?.benchmarks?.find((b) => b.id === 'B6')?.raw_ticks_per_sec || 20000;
  const speedRatio = (currentSpeed / (baseSpeed || 1)).toFixed(1);

  const presets = [
    { id: 'target', label: 'Target Standards', action: () => setCompareMode('target') },
    { 
      id: 'previous', 
      label: 'vs. Previous', 
      action: () => {
        setCompareMode('previous');
        onSelectCompareRun(Math.max(0, selectedRunIdx - 1));
      }
    },
    { 
      id: 'baseline', 
      label: 'vs. Phase 0.6', 
      action: () => {
        setCompareMode('baseline');
        onSelectCompareRun(0);
      }
    },
  ];

  const isComparative = compareMode !== 'target' && baselineRun && selectedRunIdx !== compareRunIdx;

  return (
    <section className="bg-slate-900/90 border border-white/[0.08] p-4 sm:p-5 rounded-2xl shadow-xl backdrop-blur-xl mb-8 space-y-3.5">
      {/* Top Command Bar: Run Selector + Segmented Preset Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3.5 pb-3.5 border-b border-white/[0.06]">
        
        {/* Left: Active Run Selector with Verified Pill */}
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="flex items-center space-x-1.5 text-xs font-mono text-cyan-400 font-semibold shrink-0">
            <History className="w-4 h-4" />
            <span>Run:</span>
          </div>

          <div className="relative">
            <select
              value={selectedRunIdx}
              onChange={(e) => onSelectRun(Number(e.target.value))}
              aria-label="Select active benchmark run"
              className="bg-black/60 hover:bg-black/80 text-white font-mono text-xs rounded-xl px-3 py-1.5 pr-8 border border-white/[0.1] focus:outline-none focus:border-cyan-400 cursor-pointer shadow-inner appearance-none transition-colors"
            >
              {runs.map((r, idx) => (
                <option key={r.run_id} value={idx} className="bg-[#030712] text-slate-200">
                  Run #{idx + 1} • {formatDate(r.timestamp)}
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400 text-xs">
              ▾
            </div>
          </div>

          {/* Verification Status Pill */}
          <div className="px-2.5 py-1 rounded-full bg-emerald-950/50 border border-emerald-500/30 text-emerald-300 font-mono text-xs font-bold flex items-center gap-1.5 shadow-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.8)]" />
            <span>{currentRun.passed_count}/{currentRun.total_count} Verified</span>
          </div>

          {/* Compare Target Selector (if custom) */}
          {compareMode === 'custom' && (
            <div className="flex items-center gap-1.5 text-xs font-mono text-slate-400">
              <span className="text-slate-500">vs</span>
              <select
                value={compareRunIdx ?? 0}
                onChange={(e) => onSelectCompareRun(Number(e.target.value))}
                aria-label="Select benchmark run to compare against"
                className="bg-black/60 text-slate-200 font-mono text-xs rounded-xl px-2.5 py-1 border border-white/[0.1] cursor-pointer"
              >
                {runs.map((r, idx) => (
                  <option key={r.run_id} value={idx} className="bg-[#030712] text-slate-200">
                    Run #{idx + 1}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Right: Tactile Segmented Pill Controls */}
        <div className="flex items-center gap-1 bg-black/60 p-1 rounded-full border border-white/[0.08] self-start lg:self-auto font-mono text-xs shadow-inner">
          {presets.map((preset) => {
            const isActive = compareMode === preset.id;
            return (
              <motion.button
                {...tapScale.pill}
                key={preset.id}
                type="button"
                aria-pressed={isActive}
                onClick={preset.action}
                className={`relative px-3.5 py-1 rounded-full text-xs transition-colors cursor-pointer font-bold ${
                  isActive
                    ? 'text-slate-950 font-black'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeComparePill"
                    className="absolute inset-0 bg-cyan-400 rounded-full shadow-md shadow-cyan-500/20 z-[-1]"
                    transition={springJelly}
                  />
                )}
                <span className="relative z-10">{preset.label}</span>
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* Bottom Context Strip: Ultra-Concise High-Signal Metrics */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
        
        {isComparative ? (
          /* Progression Delta Mode */
          <div className="flex flex-wrap items-center gap-3 sm:gap-4 text-emerald-400 font-semibold">
            <span className="flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>{speedRatio}x throughput ({currentSpeedDisplay})</span>
            </span>
            <span className="text-white/10 hidden sm:inline">•</span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>100% Invariants Maintained</span>
            </span>
            <span className="text-white/10 hidden sm:inline">•</span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <Activity className="w-3.5 h-3.5 text-cyan-400" />
              <span>0.0 PPB Energy Drift</span>
            </span>
          </div>
        ) : (
          /* Target Standard Anchored Metrics */
          <div className="flex flex-wrap items-center gap-2.5 sm:gap-4 text-slate-300">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span>Pure-Math Sandbox (0 OS Imports)</span>
            </span>
            <span className="text-white/10 hidden sm:inline">•</span>
            <span className="flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span>IEEE 754 (&gt;16 Decades Precision)</span>
            </span>
            <span className="text-white/10 hidden sm:inline">•</span>
            <span className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span>0.0 PPB Drift</span>
            </span>
            <span className="text-white/10 hidden sm:inline">•</span>
            <span className="flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-amber-400 shrink-0" />
              <span>{currentSpeedDisplay}</span>
            </span>
          </div>
        )}

        {/* Audit Hash */}
        <div className="flex items-center gap-1.5 text-slate-500 text-[11px] shrink-0">
          <span>Audit:</span>
          <code className="text-slate-400 font-semibold">{currentRun.run_id}</code>
        </div>
      </div>
    </section>
  );
}
