import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, BarChart3, BookOpen } from 'lucide-react';
import { tapScale } from '../lib/motion';

export default function Header({ latestRun, onOpenThesis }) {
  return (
    <header className="sticky top-0 z-50 border-b border-cyan-500/10 bg-[#030712]/90 backdrop-blur-2xl transition-all">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-14 sm:h-16 flex items-center justify-between gap-2 sm:gap-4">
        
        {/* Left: Brand Mark */}
        <div className="flex items-center space-x-2 sm:space-x-3 text-left">
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-xl sm:rounded-2xl bg-gradient-to-b from-cyan-400 to-cyan-800 p-[1px] shadow-sm shadow-cyan-500/20 shrink-0">
            <div className="w-full h-full bg-[#060D1A] rounded-[11px] sm:rounded-[15px] flex items-center justify-center">
              <Cpu className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-cyan-400" />
            </div>
          </div>
          <div className="flex flex-col font-mono leading-none">
            <div className="flex items-baseline space-x-1 sm:space-x-1.5">
              <span className="text-xs sm:text-sm font-bold tracking-tight text-white">MLUE</span>
              <span className="text-[9px] sm:text-[10px] text-cyan-400 font-semibold tracking-wider hidden xs:inline">BENCHMARK</span>
            </div>
            <span className="text-[9px] text-slate-400 font-sans hidden md:inline mt-0.5">15-Pillar Empirical Telemetry Suite</span>
          </div>
        </div>

        {/* Center: Real Substrate Telemetry Pill */}
        <div className="hidden sm:flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-black/60 border border-white/[0.08] shadow-inner font-mono text-xs text-slate-300">
          <BarChart3 className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-white font-semibold">15 Orthogonal Pillars</span>
          <span className="text-slate-600">|</span>
          <span className="text-emerald-400 font-semibold">14 Passing</span>
          <span className="text-slate-600">|</span>
          <span className="text-amber-400 font-semibold">1 Pending WASM</span>
        </div>

        {/* Right: Architecture Thesis Link & Calm Runtime Operational Indicator */}
        <div className="flex items-center space-x-2 sm:space-x-2.5 font-mono text-[11px]">
          {onOpenThesis && (
            <motion.button
              {...tapScale.button}
              type="button"
              onClick={onOpenThesis}
              aria-label="Open Architecture Thesis"
              title="MLUE Architecture Thesis"
              className="flex items-center space-x-1.5 px-2.5 sm:px-3 py-1 rounded-full bg-slate-900/70 hover:bg-slate-800/90 border border-white/[0.08] hover:border-cyan-500/30 text-slate-400 hover:text-cyan-300 transition-colors cursor-pointer shadow-sm"
            >
              <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
              <span className="hidden sm:inline">Architecture Thesis</span>
            </motion.button>
          )}

          <div 
            title="Python Substrate Headless Verification"
            className="hidden xs:flex items-center space-x-2 px-2.5 sm:px-3 py-1 rounded-full bg-slate-900/80 border border-white/[0.08] text-slate-300 shadow-sm"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_6px_rgba(52,211,153,0.8)]" />
            <span className="font-medium text-slate-300 hidden md:inline">Telemetry: 100% Live</span>
            <span className="font-medium text-slate-300 md:hidden">Live</span>
          </div>
        </div>

      </div>
    </header>
  );
}
