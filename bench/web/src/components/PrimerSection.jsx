import React from 'react';
import { Box, Cpu, Gauge } from 'lucide-react';

export default function PrimerSection() {
  return (
    <section className="mb-8 p-6 sm:p-8 rounded-2xl glass-card relative overflow-hidden">
      <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 max-w-4xl">
        <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white mb-2">
          "AI is the builder. Humans are users."
        </h2>
        <p className="text-slate-400 text-xs sm:text-sm leading-relaxed mb-6 font-mono">
          Physics-grounded declarative software substrate. Zero procedural boilerplate.
        </p>

        {/* 3 Concise Feature Chips */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          
          <div className="p-3 rounded-xl bg-ocean-950/40 border border-cyan-900/20 flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-cyan-950/60 border border-cyan-800/30">
              <Box className="w-4 h-4 text-cyan-400" />
            </div>
            <div>
              <div className="text-xs font-semibold text-slate-200">Universal Pool</div>
              <div className="text-[11px] text-slate-500 font-mono">Reusable primitives</div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-ocean-950/40 border border-cyan-900/20 flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-emerald-950/60 border border-emerald-800/30">
              <Cpu className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <div className="text-xs font-semibold text-slate-200">Deterministic Core</div>
              <div className="text-[11px] text-slate-500 font-mono">Bit-exact physics</div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-ocean-950/40 border border-cyan-900/20 flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-sand-950/60 border border-sand-800/30">
              <Gauge className="w-4 h-4 text-sand-400" />
            </div>
            <div>
              <div className="text-xs font-semibold text-slate-200">Domain Telemetry</div>
              <div className="text-[11px] text-slate-500 font-mono">Multi-format metrics</div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
