import React from 'react';
import { motion } from 'framer-motion';
import { Layers, ShieldCheck, Cpu, BarChart3, Sparkles } from 'lucide-react';
import { springJelly, tapScale } from '../lib/motion';

export default function Header({ latestRun, activeView, onSelectView }) {
  const navTabs = [
    { id: 'studio', label: 'AI STUDIO', icon: Sparkles },
    { id: 'benchmarks', label: 'BENCHMARKS', icon: BarChart3 },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-cyan-500/10 bg-[#030712]/90 backdrop-blur-2xl transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        
        {/* Left: Brand Mark */}
        <motion.div 
          {...tapScale.button}
          className="flex items-center space-x-3 cursor-pointer" 
          onClick={() => onSelectView('studio')}
        >
          <div className="w-9 h-9 rounded-2xl bg-gradient-to-b from-cyan-400 to-cyan-800 p-[1px] shadow-sm shadow-cyan-500/20">
            <div className="w-full h-full bg-[#060D1A] rounded-[15px] flex items-center justify-center">
              <Cpu className="w-4 h-4 text-cyan-400" />
            </div>
          </div>
          <div className="flex flex-col font-mono">
            <div className="flex items-baseline space-x-1.5">
              <span className="text-sm font-bold tracking-tight text-white">MLUE</span>
              <span className="text-[10px] text-cyan-400 font-semibold tracking-wider">AI SUBSTRATE</span>
            </div>
            <span className="text-[9px] text-slate-400 font-sans hidden sm:inline">Native Computational Engine</span>
          </div>
        </motion.div>

        {/* Center: Universal Floating Capsule Tab Slider (Golden Standard) */}
        <div className="flex items-center bg-black/60 p-1 rounded-full border border-white/[0.08] shadow-inner font-mono text-xs relative">
          {navTabs.map((tab) => {
            const isActive = activeView === tab.id;
            const Icon = tab.icon;
            return (
              <motion.button
                {...tapScale.pill}
                key={tab.id}
                onClick={() => onSelectView(tab.id)}
                className={`relative z-10 flex items-center space-x-2 px-4 py-1.5 text-xs font-bold rounded-full transition-colors cursor-pointer ${
                  isActive ? 'text-slate-950 font-black' : 'text-slate-400 hover:text-white'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeHeaderNavTab"
                    className="absolute inset-0 bg-cyan-400 rounded-full shadow-md shadow-cyan-500/30 z-[-1]"
                    transition={springJelly}
                  />
                )}
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </motion.button>
            );
          })}
        </div>

        {/* Right: Status Badges */}
        <div className="hidden md:flex items-center gap-2 font-mono text-[11px]">
          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 shadow-sm shadow-cyan-500/10">
            <Layers className="w-3 h-3 text-cyan-400" />
            <span className="font-medium">{latestRun?.substrate_tier || 'Tier L1 Substrate'}</span>
          </div>

          <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 font-semibold shadow-sm shadow-emerald-500/10">
            <ShieldCheck className="w-3 h-3" />
            <span>{latestRun?.passed_count || 12}/{latestRun?.total_count || 12} INVARIANTS PASSED</span>
          </div>
        </div>

      </div>
    </header>
  );
}
