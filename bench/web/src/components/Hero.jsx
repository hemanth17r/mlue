import React from 'react';
import { Sparkles, Shield, Zap, Activity, Layers } from 'lucide-react';

export default function Hero({ latestRun }) {
  return (
    <section className="pt-6 pb-8 text-center max-w-4xl mx-auto">
      
      {/* Micro Eyebrow */}
      <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/40 border border-cyan-500/20 text-[11px] font-mono text-cyan-300 mb-4 shadow-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_8px_rgba(34,211,238,0.8)]" />
        <span>10-Pillar Multi-Format Architectural Audit</span>
      </div>

      {/* Main Apple Headline */}
      <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight apple-ocean-text mb-3">
        Physics-Grounded. Declarative. Substrate.
      </h1>

      {/* Subline Axiom */}
      <p className="text-sm sm:text-base text-slate-400 font-mono max-w-2xl mx-auto mb-6">
        "AI is the builder. Humans are users." Zero procedural boilerplate. 100% empirical telemetry.
      </p>

      {/* Hero Key Metrics Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 max-w-3xl mx-auto">
        
        <div className="p-3 rounded-xl apple-glass text-left">
          <div className="text-[10px] font-mono uppercase text-slate-500 tracking-wider">Simulation Speed</div>
          <div className="text-lg font-bold font-mono text-amber-400 mt-0.5">30.1k <span className="text-[11px] font-normal text-slate-400">ticks/s</span></div>
        </div>

        <div className="p-3 rounded-xl apple-glass text-left">
          <div className="text-[10px] font-mono uppercase text-slate-500 tracking-wider">Energy Drift</div>
          <div className="text-lg font-bold font-mono text-emerald-400 mt-0.5">0.0 <span className="text-[11px] font-normal text-slate-400">PPB</span></div>
        </div>

        <div className="p-3 rounded-xl apple-glass text-left">
          <div className="text-[10px] font-mono uppercase text-slate-500 tracking-wider">Spatial Precision</div>
          <div className="text-lg font-bold font-mono text-cyan-300 mt-0.5">&gt;16.0 <span className="text-[11px] font-normal text-slate-400">Decades</span></div>
        </div>

        <div className="p-3 rounded-xl apple-glass text-left">
          <div className="text-[10px] font-mono uppercase text-slate-500 tracking-wider">Defect Rejection</div>
          <div className="text-lg font-bold font-mono text-indigo-300 mt-0.5">10/10 <span className="text-[11px] font-normal text-slate-400">100% Blocked</span></div>
        </div>

      </div>

    </section>
  );
}
