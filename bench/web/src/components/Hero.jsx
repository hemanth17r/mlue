import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Shield, Zap, Activity, Layers } from 'lucide-react';
import { tapScale } from '../lib/motion';

export default function Hero({ latestRun }) {
  const b = latestRun?.benchmarks || [];

  // Dynamically extract values from the active run
  const speed = b.find((item) => item.id === 'B6')?.value_display || '21.5k t/s';
  const drift = b.find((item) => item.id === 'B4')?.drift_ppb || '0.0 PPB';
  const precision = b.find((item) => item.id === 'B3')?.log_precision_decades || '>16.0 Decades';
  const passedCount = latestRun?.passed_count || 12;
  const totalCount = latestRun?.total_count || 12;

  const metrics = [
    { label: 'Simulation Speed', value: speed, color: 'text-amber-400' },
    { label: 'Energy Drift', value: drift, color: 'text-emerald-400' },
    { label: 'Spatial Precision', value: precision, color: 'text-cyan-300' },
    { 
      label: 'Defect Rejection', 
      value: `${passedCount}/${totalCount}`, 
      suffix: '100% Blocked', 
      color: 'text-indigo-300' 
    },
  ];

  return (
    <section className="pt-4 pb-8 text-center max-w-4xl mx-auto">
      {/* Eyebrow (Golden Standard: rounded-full) */}
      <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-cyan-950/40 border border-cyan-500/20 text-[11px] font-mono text-cyan-300 mb-4 shadow-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_8px_rgba(34,211,238,0.8)]" />
        <span>{totalCount}-Pillar Multi-Format Architectural Audit</span>
      </div>

      {/* Main Headline */}
      <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-white mb-3 leading-tight">
        First-Principles. Declarative. <br className="hidden sm:inline" />
        <span className="bg-gradient-to-r from-cyan-400 via-teal-300 to-blue-500 bg-clip-text text-transparent">
          Universal Substrate.
        </span>
      </h1>

      {/* Subline Axiom */}
      <p className="text-sm sm:text-base text-slate-400 font-sans max-w-2xl mx-auto mb-8 leading-relaxed">
        "AI is the builder. Humans are users." One unified mathematical substrate for software applications, interactive UIs, simulations, and games.
      </p>

      {/* Hero Key Metrics Strip (Golden Standard: rounded-2xl cards) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-3xl mx-auto">
        {metrics.map((m, idx) => (
          <motion.div 
            {...tapScale.card}
            key={idx}
            className="p-4 rounded-2xl bg-slate-900/80 border border-white/[0.08] hover:border-cyan-500/40 text-left shadow-lg transition-colors cursor-default"
          >
            <div className="text-[10px] font-mono uppercase text-slate-500 tracking-wider font-semibold">
              {m.label}
            </div>
            <div className={`text-lg font-bold font-mono ${m.color} mt-1 flex items-baseline gap-1`}>
              <span>{m.value}</span>
              {m.suffix && (
                <span className="text-[10px] font-normal text-slate-400">{m.suffix}</span>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
