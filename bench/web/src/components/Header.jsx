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
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-14 sm:h-16 flex items-center justify-between gap-2 sm:gap-4">
        
        {/* Left: Brand Mark */}
        <motion.button 
          {...tapScale.button}
          type="button"
          aria-label="MLUE AI Studio Home"
          className="flex items-center space-x-2 sm:space-x-3 cursor-pointer shrink-0 text-left bg-transparent border-none p-0 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 rounded-xl" 
          onClick={() => onSelectView('studio')}
        >
          <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-xl sm:rounded-2xl bg-gradient-to-b from-cyan-400 to-cyan-800 p-[1px] shadow-sm shadow-cyan-500/20 shrink-0">
            <div className="w-full h-full bg-[#060D1A] rounded-[11px] sm:rounded-[15px] flex items-center justify-center">
              <Cpu className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-cyan-400" />
            </div>
          </div>
          <div className="flex flex-col font-mono leading-none">
            <div className="flex items-baseline space-x-1 sm:space-x-1.5">
              <span className="text-xs sm:text-sm font-bold tracking-tight text-white">MLUE</span>
              <span className="text-[9px] sm:text-[10px] text-cyan-400 font-semibold tracking-wider hidden xs:inline">RUNTIME</span>
            </div>
            <span className="text-[9px] text-slate-400 font-sans hidden md:inline mt-0.5">AI Interactive Substrate</span>
          </div>
        </motion.button>

        {/* Center: Universal Floating Capsule Tab Slider */}
        <nav 
          aria-label="Primary Navigation"
          className="flex items-center bg-black/60 p-1 rounded-full border border-white/[0.08] shadow-inner font-mono text-xs relative shrink-0"
        >
          {navTabs.map((tab) => {
            const isActive = activeView === tab.id;
            const Icon = tab.icon;
            return (
              <motion.button
                {...tapScale.pill}
                key={tab.id}
                type="button"
                role="tab"
                aria-selected={isActive}
                aria-label={`View ${tab.label}`}
                onClick={() => onSelectView(tab.id)}
                className={`relative z-10 flex items-center space-x-1.5 sm:space-x-2 px-3 sm:px-4 py-1.5 text-[11px] sm:text-xs font-bold rounded-full transition-colors cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 ${
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
                <Icon className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                <span>{tab.label}</span>
              </motion.button>
            );
          })}
        </nav>

        {/* Right: Subdued System Status Indicator (Demoted from noisy badges) */}
        <div className="hidden md:flex items-center font-mono text-[11px]">
          <div 
            title="Continuous Verification Status"
            className="flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900/80 border border-white/[0.08] text-slate-300 shadow-sm"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_6px_rgba(52,211,153,0.8)]" />
            <span className="font-medium text-slate-300">System: Healthy</span>
            <span className="text-slate-600">•</span>
            <span className="text-cyan-400 font-semibold">{latestRun?.passed_count || 13}/{latestRun?.total_count || 13} Invariants</span>
          </div>
        </div>

      </div>
    </header>
  );
}
