import React from 'react';
import { Layers, ShieldCheck, Cpu } from 'lucide-react';

export default function Header({ latestRun }) {
  return (
    <header className="sticky top-0 z-50 border-b border-cyan-500/10 bg-[#030712]/80 backdrop-blur-2xl transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        
        {/* Left: Brand Mark */}
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-b from-cyan-400 to-cyan-800 p-[1px] shadow-sm shadow-cyan-500/20">
            <div className="w-full h-full bg-[#060D1A] rounded-[7px] flex items-center justify-center">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            </div>
          </div>
          <div className="flex items-baseline space-x-1.5 font-mono">
            <span className="text-xs font-semibold tracking-tight text-white">MLUE</span>
            <span className="text-[10px] text-cyan-400/80 font-medium tracking-wider">BENCHMARKS</span>
          </div>
        </div>

        {/* Right: Status Pills */}
        <div className="flex items-center gap-2 font-mono text-[11px]">
          
          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-white/[0.03] border border-white/[0.08] text-slate-300">
            <span className="w-1.5 h-1.5 rounded-full bg-sand-400 shadow-[0_0_6px_rgba(245,158,11,0.6)]" />
            <span>{latestRun?.mlue_phase || 'Phase 1.6'}</span>
          </div>

          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 shadow-sm shadow-cyan-500/10">
            <Layers className="w-3 h-3 text-cyan-400" />
            <span className="font-medium">{latestRun?.substrate_tier || 'Tier L1 Substrate'}</span>
          </div>

          <a
            href="#playground"
            className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-300 font-semibold transition shadow-sm shadow-cyan-500/20"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
            <span>PLAY LIVE</span>
          </a>

          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 font-semibold shadow-sm shadow-emerald-500/10">
            <ShieldCheck className="w-3 h-3" />
            <span>{latestRun?.passed_count || 12}/{latestRun?.total_count || 12} INVARIANTS PASSED</span>
          </div>

        </div>

      </div>
    </header>
  );
}
