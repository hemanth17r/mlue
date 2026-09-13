import React from 'react';
import { motion } from 'framer-motion';
import { 
  History, 
  ShieldCheck, 
  Compass, 
  Activity, 
  Zap, 
  TrendingUp,
  GitCompare,
  CheckCircle2,
  SlidersHorizontal
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
  const baselineRun = compareRunIdx !== null && runs[compareRunIdx] ? runs[compareRunIdx] : runs[0];

  // Helper to extract clean phase name
  const getPhaseShort = (phaseStr) => {
    if (!phaseStr) return 'Baseline';
    return phaseStr.split('(')[0].trim();
  };

  // Format date helper: "Sep 13, 11:58 AM"
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

  // Find key milestone indices across runs
  const idxV25 = runs.findIndex((r) => r.mlue_phase?.includes('v2.5.0'));
  const v25Index = idxV25 >= 0 ? idxV25 : Math.max(0, runs.length - 3);

  const idxP16 = runs.findIndex((r) => r.mlue_phase?.includes('Phase 1.6'));
  const p16Index = idxP16 >= 0 ? idxP16 : 14;

  const currentSpeed = currentRun.benchmarks?.find((b) => b.id === 'B6')?.raw_ticks_per_sec || 11648;
  const currentSpeedDisplay = currentRun.benchmarks?.find((b) => b.id === 'B6')?.value_display || '11.6k t/s';
  const baseSpeed = baselineRun?.benchmarks?.find((b) => b.id === 'B6')?.raw_ticks_per_sec || 20000;
  const baseSpeedDisplay = baselineRun?.benchmarks?.find((b) => b.id === 'B6')?.value_display || '20.0k t/s';
  const speedRatio = (currentSpeed / (baseSpeed || 1)).toFixed(2);

  const currentChurn = currentRun.benchmarks?.find((b) => b.id === 'B7')?.bytes_per_step || '0.62 B/tick';
  const baseChurn = baselineRun?.benchmarks?.find((b) => b.id === 'B7')?.bytes_per_step || '0.72 B/tick';

  const currentDrift = currentRun.benchmarks?.find((b) => b.id === 'B4')?.drift_ppb || '0.0 PPB';
  const baseDrift = baselineRun?.benchmarks?.find((b) => b.id === 'B4')?.drift_ppb || '0.0 PPB';

  const presets = [
    { 
      id: 'target', 
      label: 'Target Standards', 
      action: () => setCompareMode('target') 
    },
    { 
      id: 'previous', 
      label: 'vs. Previous Run', 
      action: () => {
        setCompareMode('previous');
        onSelectCompareRun(Math.max(0, selectedRunIdx - 1));
      }
    },
    { 
      id: 'v25', 
      label: 'vs. v2.5 Capstone', 
      action: () => {
        setCompareMode('v25');
        onSelectCompareRun(v25Index);
      }
    },
    { 
      id: 'p16', 
      label: 'vs. Phase 1.6 SIMD', 
      action: () => {
        setCompareMode('p16');
        onSelectCompareRun(p16Index);
      }
    },
    { 
      id: 'custom', 
      label: 'Custom Compare...', 
      action: () => {
        setCompareMode('custom');
        if (compareRunIdx === null || compareRunIdx === selectedRunIdx) {
          onSelectCompareRun(Math.max(0, selectedRunIdx - 1));
        }
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
            <span>Active Run:</span>
          </div>

          <div className="relative">
            <select
              value={selectedRunIdx}
              onChange={(e) => onSelectRun(Number(e.target.value))}
              aria-label="Select active benchmark run"
              className="bg-black/60 hover:bg-black/80 text-white font-mono text-xs rounded-xl px-3 py-1.5 pr-8 border border-white/[0.1] focus:outline-none focus:border-cyan-400 cursor-pointer shadow-inner appearance-none transition-colors max-w-[280px] sm:max-w-xs truncate"
            >
              {runs.map((r, idx) => (
                <option key={r.run_id} value={idx} className="bg-[#030712] text-slate-200">
                  Run #{idx + 1} • {getPhaseShort(r.mlue_phase)} • {formatDate(r.timestamp)}
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

          {/* Compare Target Selector (when in custom mode) */}
          {compareMode === 'custom' && (
            <div className="flex items-center gap-1.5 text-xs font-mono text-slate-400 pl-1 border-l border-white/[0.1]">
              <span className="text-amber-400 font-bold">vs</span>
              <div className="relative">
                <select
                  value={compareRunIdx ?? 0}
                  onChange={(e) => onSelectCompareRun(Number(e.target.value))}
                  aria-label="Select benchmark run to compare against"
                  className="bg-black/80 text-amber-300 font-mono text-xs rounded-xl px-3 py-1.5 pr-7 border border-amber-500/30 focus:outline-none focus:border-amber-400 cursor-pointer max-w-[240px] truncate"
                >
                  {runs.map((r, idx) => (
                    <option key={r.run_id} value={idx} className="bg-[#030712] text-slate-200">
                      Run #{idx + 1} • {getPhaseShort(r.mlue_phase)}
                    </option>
                  ))}
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-amber-400 text-xs">
                  ▾
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right: Tactile Segmented Pill Controls */}
        <div className="flex flex-wrap items-center gap-1 bg-black/60 p-1 rounded-2xl sm:rounded-full border border-white/[0.08] font-mono text-xs shadow-inner">
          {presets.map((preset) => {
            const isActive = compareMode === preset.id;
            return (
              <motion.button
                {...tapScale.pill}
                key={preset.id}
                type="button"
                aria-pressed={isActive}
                onClick={preset.action}
                className={`relative px-3 py-1 rounded-full text-xs transition-colors cursor-pointer font-bold whitespace-nowrap ${
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

      {/* Bottom Context Strip: Real-time Telemetry Progression */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
        
        {isComparative ? (
          /* Progression Delta Mode */
          <div className="flex flex-wrap items-center gap-2.5 sm:gap-4 text-xs">
            <div className="flex items-center gap-1.5 text-cyan-300 font-bold bg-cyan-950/40 px-2.5 py-0.5 rounded-lg border border-cyan-500/30">
              <GitCompare className="w-3.5 h-3.5 text-cyan-400" />
              <span>
                Run #{selectedRunIdx + 1} ({getPhaseShort(currentRun.mlue_phase)}) vs Run #{compareRunIdx + 1} ({getPhaseShort(baselineRun.mlue_phase)})
              </span>
            </div>

            <span className="text-white/10 hidden sm:inline">•</span>

            <span className={`flex items-center gap-1.5 font-semibold ${Number(speedRatio) >= 1 ? 'text-emerald-400' : 'text-amber-400'}`}>
              <TrendingUp className="w-3.5 h-3.5" />
              <span>{speedRatio}x throughput ({currentSpeedDisplay} vs {baseSpeedDisplay})</span>
            </span>

            <span className="text-white/10 hidden sm:inline">•</span>

            <span className="flex items-center gap-1.5 text-slate-300">
              <Activity className="w-3.5 h-3.5 text-teal-400" />
              <span>Churn: {currentChurn} vs {baseChurn}</span>
            </span>

            <span className="text-white/10 hidden sm:inline">•</span>

            <span className="flex items-center gap-1.5 text-slate-300">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Drift: {currentDrift} vs {baseDrift}</span>
            </span>

            <span className="text-white/10 hidden sm:inline">•</span>

            <span className="flex items-center gap-1.5 text-indigo-300 font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
              <span>{currentRun.passed_count}/{currentRun.total_count} vs {baselineRun.passed_count}/{baselineRun.total_count} Passing</span>
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
              <span>0.0 PPB Symplectic Drift</span>
            </span>
            <span className="text-white/10 hidden sm:inline">•</span>
            <span className="flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-amber-400 shrink-0" />
              <span>{currentSpeedDisplay}</span>
            </span>
          </div>
        )}

        {/* Audit Run ID */}
        <div className="flex items-center gap-1.5 text-slate-500 text-[11px] shrink-0">
          <span>Audit:</span>
          <code className="text-slate-400 font-semibold">{currentRun.run_id}</code>
        </div>
      </div>
    </section>
  );
}
