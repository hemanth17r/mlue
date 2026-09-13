import React from 'react';
import { motion } from 'framer-motion';
import { tapScale } from '../lib/motion';

export default function Hero({ latestRun }) {
  const b = latestRun?.benchmarks || [];

  // Dynamically extract values from the active run
  const rawSpeed = b.find((item) => item.id === 'B6')?.value_display || '21.5k t/s';
  const speed = rawSpeed.split('(')[0].trim();
  const drift = b.find((item) => item.id === 'B4')?.drift_ppb || '0.0 PPB';
  const precision = b.find((item) => item.id === 'B3')?.log_precision_decades || '>16.0 Decades';
  const passedCount = latestRun?.passed_count || 14;
  const totalCount = latestRun?.total_count || 15;

  const metrics = [
    { 
      label: '⚡ Simulation Speed', 
      value: speed, 
      color: 'text-amber-400',
      definition: 'Evaluation throughput per CPU core'
    },
    { 
      label: '🛡️ Kinetic Drift', 
      value: drift, 
      color: 'text-emerald-400',
      definition: 'Symplectic conservation in closed systems'
    },
    { 
      label: '🎯 Spatial Precision', 
      value: precision, 
      color: 'text-cyan-300',
      definition: 'Normalized coordinate invariance [0, 1]'
    },
    { 
      label: '✓ Formal Proofs', 
      value: `${passedCount}/${totalCount}`, 
      suffix: 'Passing', 
      color: 'text-indigo-300',
      definition: 'Static boundary & safety verification'
    },
  ];

  return (
    <section className="pt-2 sm:pt-4 pb-4 sm:pb-6 text-center max-w-4xl mx-auto px-2">
      {/* Main Headline - Direct punchy title immediately followed by main metric cards */}
      <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white mb-6 sm:mb-8 leading-tight">
        Bit-exact. Microsecond fast. <br className="hidden sm:inline" />
        <span className="bg-gradient-to-r from-cyan-400 via-teal-300 to-blue-500 bg-clip-text text-transparent">
          Zero OS dependencies.
        </span>
      </h1>

      {/* Hero Key Metrics Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3 max-w-3xl mx-auto">
        {metrics.map((m, idx) => (
          <motion.div 
            {...tapScale.card}
            key={idx}
            className="p-3.5 sm:p-4 rounded-2xl bg-slate-900/80 border border-white/[0.08] hover:border-cyan-500/40 text-left shadow-lg transition-colors cursor-default flex flex-col justify-between min-h-[110px]"
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
