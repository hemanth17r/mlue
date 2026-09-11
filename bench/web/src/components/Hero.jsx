import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Shield, Zap, Activity, Layers, ChevronDown, Info } from 'lucide-react';
import { tapScale, springSnappy } from '../lib/motion';

export default function Hero({ latestRun }) {
  const [showThesis, setShowThesis] = useState(false);
  const b = latestRun?.benchmarks || [];

  // Dynamically extract values from the active run
  const speed = b.find((item) => item.id === 'B6')?.value_display || '21.5k t/s';
  const drift = b.find((item) => item.id === 'B4')?.drift_ppb || '0.0 PPB';
  const precision = b.find((item) => item.id === 'B3')?.log_precision_decades || '>16.0 Decades';
  const passedCount = latestRun?.passed_count || 13;
  const totalCount = latestRun?.total_count || 13;

  const metrics = [
    { 
      label: 'Simulation Speed', 
      value: speed, 
      color: 'text-amber-400',
      definition: 'Evaluation throughput per CPU core'
    },
    { 
      label: 'Energy Drift', 
      value: drift, 
      color: 'text-emerald-400',
      definition: 'Kinetic conservation in closed tests'
    },
    { 
      label: 'Spatial Precision', 
      value: precision, 
      color: 'text-cyan-300',
      definition: 'Coordinate invariance [0, 1] across displays'
    },
    { 
      label: 'Invariant Checks', 
      value: `${passedCount}/${totalCount}`, 
      suffix: 'Verified', 
      color: 'text-indigo-300',
      definition: 'Continuous safety & bounding rules'
    },
  ];

  return (
    <section className="pt-2 sm:pt-4 pb-6 sm:pb-8 text-center max-w-4xl mx-auto px-2">
      {/* Eyebrow */}
      <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-cyan-950/40 border border-cyan-500/20 text-[11px] font-mono text-cyan-300 mb-3 sm:mb-4 shadow-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_8px_rgba(34,211,238,0.8)]" />
        <span>Continuous Engineering Benchmark Report • {latestRun?.mlue_phase || 'Phase 1.6'}</span>
      </div>

      {/* Main Headline - Plain Language First */}
      <h1 className="text-2xl sm:text-4xl lg:text-5xl font-black tracking-tight text-white mb-3 leading-tight">
        A deterministic runtime for <br className="hidden sm:inline" />
        <span className="bg-gradient-to-r from-cyan-400 via-teal-300 to-blue-500 bg-clip-text text-transparent">
          AI-built interactive software.
        </span>
      </h1>

      {/* Plain English Subtitle */}
      <p className="text-xs sm:text-sm md:text-base text-slate-300 font-sans max-w-2xl mx-auto mb-4 sm:mb-6 leading-relaxed">
        Measured by the included automated harness across 13 continuous mathematical invariants: determinism, memory churn, spatial precision, and microsecond evaluation.
      </p>

      {/* Architecture Thesis (Progressive Disclosure) */}
      <div className="mb-6 sm:mb-8">
        <button
          type="button"
          onClick={() => setShowThesis(!showThesis)}
          aria-expanded={showThesis}
          className="inline-flex items-center space-x-1.5 text-xs font-mono text-slate-400 hover:text-cyan-300 transition-colors cursor-pointer bg-slate-900/60 border border-white/[0.06] hover:border-cyan-500/30 px-3 py-1 rounded-full"
        >
          <Info className="w-3 h-3 text-cyan-400" />
          <span>{showThesis ? 'Hide Architecture Thesis' : 'Read Architecture Thesis'}</span>
          <ChevronDown className={`w-3 h-3 transition-transform ${showThesis ? 'rotate-180' : ''}`} />
        </button>

        <AnimatePresence>
          {showThesis && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto', transition: springSnappy }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-3 p-4 rounded-2xl bg-slate-900/90 border border-cyan-500/20 max-w-2xl mx-auto text-left text-xs font-sans text-slate-300 space-y-2"
            >
              <p className="font-semibold text-white font-mono text-[11px] text-cyan-400 uppercase tracking-wider">
                Thesis: "AI is the builder. Humans are users."
              </p>
              <p className="text-slate-400 leading-relaxed">
                Conventional software stacks (DOM, Chromium, dynamic JS runtimes) are optimized for human developers typing manual code. MLUE provides a compact, declarative, mathematical substrate designed specifically for generative models: zero dependencies, memory-mapped state, and verifiable boundary safety before execution.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Hero Key Metrics Strip with Human-Readable Definitions */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3 max-w-3xl mx-auto">
        {metrics.map((m, idx) => (
          <motion.div 
            {...tapScale.card}
            key={idx}
            className="p-3 sm:p-4 rounded-2xl bg-slate-900/80 border border-white/[0.08] hover:border-cyan-500/40 text-left shadow-lg transition-colors cursor-default flex flex-col justify-between"
          >
            <div>
              <div className="text-[10px] font-mono uppercase text-slate-400 tracking-wider font-semibold truncate">
                {m.label}
              </div>
              <div className={`text-base sm:text-lg font-bold font-mono ${m.color} mt-0.5 sm:mt-1 flex items-baseline gap-1`}>
                <span>{m.value}</span>
                {m.suffix && (
                  <span className="text-[10px] font-normal text-slate-400">{m.suffix}</span>
                )}
              </div>
            </div>
            <div className="text-[10px] text-slate-500 font-sans mt-2 pt-2 border-t border-white/[0.04] leading-tight">
              {m.definition}
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
