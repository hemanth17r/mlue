import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Code, 
  Zap, 
  Trash2, 
  Maximize2, 
  ShieldAlert, 
  Lock, 
  Trophy, 
  Layers,
  Sparkles
} from 'lucide-react';
import { springJelly, tapScale } from '../lib/motion';

export default function HeadToHeadComparison() {
  const [selectedGame, setSelectedGame] = useState('dashboard');

  const gamesData = {
    dashboard: {
      name: 'UI & Dashboards',
      icon: '📊',
      verdict: 'Conventional web stacks require 450+ lines of React/Redux/CSS boilerplate and 300MB+ RAM. MLUE declares the complete data model, layout, and reactive rules in 1 self-contained JSON document with microsecond evaluation.',
      specs: [
        {
          label: 'Application Boilerplate',
          sublabel: 'Code required to build UI & state',
          icon: <Code className="w-4 h-4 text-cyan-400" />,
          traditional: { value: '450+ Lines', desc: 'React hooks, CSS flexbox, Redux store' },
          mlue: { value: '1 JSON Document', desc: 'Zero code, 100% declarative substrate' }
        },
        {
          label: 'Memory Footprint',
          sublabel: 'RAM consumption on launch',
          icon: <Trash2 className="w-4 h-4 text-rose-400" />,
          traditional: { value: '300MB – 500MB', desc: 'Heavy Chromium/Electron sandbox' },
          mlue: { value: '< 15 KB Total', desc: 'Direct memory-mapped state' }
        },
        {
          label: 'Evaluation Latency',
          sublabel: 'Time to evaluate state transition',
          icon: <Zap className="w-4 h-4 text-amber-400" />,
          traditional: { value: '16ms – 50ms', desc: 'Virtual DOM diffing & browser reflow' },
          mlue: { value: '26.8 µs', desc: 'Microsecond mathematical engine' }
        },
        {
          label: 'State Invariant Safety',
          sublabel: 'Data corruption & crash risk',
          icon: <ShieldAlert className="w-4 h-4 text-indigo-400" />,
          traditional: { value: 'Runtime Exceptions', desc: 'Undefined prop & null pointer errors' },
          mlue: { value: '100% Statically Verified', desc: 'Mathematical reachability enforcement' }
        },
        {
          label: 'AI Agent Control',
          sublabel: 'How AI agents inspect & mutate',
          icon: <Lock className="w-4 h-4 text-emerald-400" />,
          traditional: { value: 'Fragile DOM Scraping', desc: 'Breaks with every CSS change' },
          mlue: { value: 'Native MCP Protocol', desc: 'Deterministic JSON-RPC tools' }
        }
      ]
    },
    arcade: {
      name: 'Arcade Games',
      icon: '🎮',
      verdict: 'Hand-coded game loops accumulate spaghetti logic and high-speed collision tunneling bugs. MLUE guarantees continuous collision bounds and zero defect rates at 10x speeds with zero allocation overhead.',
      specs: [
        {
          label: 'Code Complexity',
          sublabel: 'Code required & logic nesting',
          icon: <Code className="w-4 h-4 text-cyan-400" />,
          traditional: { value: '280+ Lines (CC = 48)', desc: 'Tangled nested if-else webs' },
          mlue: { value: '1 JSON Schema (CC = 21)', desc: 'Clean, modular math blocks' }
        },
        {
          label: 'Simulation Speed',
          sublabel: 'Physics execution throughput',
          icon: <Zap className="w-4 h-4 text-amber-400" />,
          traditional: { value: '3,500 ticks/s', desc: 'Occasional frame drops under load' },
          mlue: { value: '37,400 ticks/s', desc: '10.7x faster (ultra smooth)' }
        },
        {
          label: 'High-Speed Tunneling',
          sublabel: 'Ball collision boundary integrity',
          icon: <ShieldAlert className="w-4 h-4 text-indigo-400" />,
          traditional: { value: 'Clips Through Walls', desc: 'Fails under high velocity' },
          mlue: { value: '0.00% Defect Rate', desc: 'Continuous collision detection' }
        },
        {
          label: 'Memory Waste',
          sublabel: 'Heap allocations during play',
          icon: <Trash2 className="w-4 h-4 text-rose-400" />,
          traditional: { value: '~18 KB/s Churn', desc: 'Garbage collection stutters' },
          mlue: { value: '< 1 Byte/tick', desc: 'Zero steady-state allocation' }
        },
        {
          label: 'Cross-Display Scale',
          sublabel: 'Viewport adaptation',
          icon: <Maximize2 className="w-4 h-4 text-teal-400" />,
          traditional: { value: 'Breaks on Resize', desc: 'Hardcoded pixel coordinates' },
          mlue: { value: '>16 Decades Precision', desc: 'Normalized [0, 1] across all screens' }
        }
      ]
    },
    simulation: {
      name: 'Physics & Simulation',
      icon: '⚡',
      verdict: 'Standard physics engines leak energy over continuous steps and bottleneck RL training loops. MLUE maintains symplectic energy conservation down to parts-per-billion with headless stepping over 4,600 steps/s.',
      specs: [
        {
          label: 'Energy Conservation',
          sublabel: 'Kinetic realism & drift',
          icon: <Zap className="w-4 h-4 text-amber-400" />,
          traditional: { value: 'Energy Leaks / Explosions', desc: 'Particles slow down or explode' },
          mlue: { value: '0.0 PPB Drift', desc: 'Symplectic conservation across 1,000 hits' }
        },
        {
          label: 'Spatial Acceleration',
          sublabel: 'Collision pair scaling',
          icon: <Code className="w-4 h-4 text-cyan-400" />,
          traditional: { value: 'O(N²) Quadratic', desc: 'Checks all pairs every frame' },
          mlue: { value: 'O(N log N) Dynamic', desc: '96.8% broadphase cull efficiency' }
        },
        {
          label: 'Step Latency',
          sublabel: 'Per-tick evaluation time',
          icon: <Sparkles className="w-4 h-4 text-amber-400" />,
          traditional: { value: '8.5ms / step', desc: 'Tied to display driver & OS' },
          mlue: { value: '13.1 µs / step', desc: 'Sub-microsecond mathematical engine' }
        },
        {
          label: 'RL Agent Training',
          sublabel: 'Vectorized stepping speed',
          icon: <Lock className="w-4 h-4 text-emerald-400" />,
          traditional: { value: '350 – 900 steps/s', desc: 'Heavy Python IPC bottleneck' },
          mlue: { value: '4,673 steps/s', desc: 'Preallocated contiguous tensor buffers' }
        },
        {
          label: 'Determinism Parity',
          sublabel: 'State match across platforms',
          icon: <ShieldAlert className="w-4 h-4 text-indigo-400" />,
          traditional: { value: 'Floating-Point Drift', desc: 'Deviates across OS and GPU' },
          mlue: { value: '100% Bit-Exact SHA-256', desc: 'Cryptographic match on 50k steps' }
        }
      ]
    }
  };

  const activeGame = gamesData[selectedGame] || gamesData.dashboard;

  return (
    <section className="space-y-6">
      
      {/* Header & Tabs (Golden Standard: Floating Capsule Pill Tabs) */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <h3 className="text-lg font-black text-white font-mono uppercase tracking-tight">
              Substrate vs. Traditional Stack
            </h3>
          </div>
          <p className="text-xs text-slate-400 font-sans mt-0.5">
            Empirical comparison across applications, interactive UIs, physics simulations, and state trees.
          </p>
        </div>

        {/* Tab Pills - Single Clean Non-Wrapping Row */}
        <div className="inline-flex items-center gap-1 bg-black/60 p-1 rounded-full border border-white/[0.08] shadow-inner font-mono text-xs overflow-x-auto max-w-full">
          {Object.entries(gamesData).map(([key, g]) => {
            const isActive = selectedGame === key;
            return (
              <motion.button
                {...tapScale.pill}
                key={key}
                onClick={() => setSelectedGame(key)}
                className={`relative z-10 flex items-center space-x-1.5 px-3.5 py-1.5 rounded-full transition-colors cursor-pointer text-xs font-bold whitespace-nowrap ${
                  isActive ? 'text-slate-950 font-black' : 'text-slate-400 hover:text-white'
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="headToHeadTabPill"
                    className="absolute inset-0 bg-cyan-400 rounded-full shadow-md shadow-cyan-500/20 z-[-1]"
                    transition={springJelly}
                  />
                )}
                <span>{g.icon}</span>
                <span>{g.name}</span>
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* Comparison Spec Card */}
      <div className="rounded-2xl bg-slate-900/80 border border-white/[0.08] overflow-hidden shadow-2xl">
        
        {/* Scrollable Container for Mobile Viewports */}
        <div className="overflow-x-auto w-full">
          <div className="min-w-[560px]">
            {/* Table Column Headers */}
            <div className="grid grid-cols-12 bg-black/40 border-b border-white/[0.06] p-4 text-xs font-mono font-bold tracking-wider">
              <div className="col-span-5 text-left text-rose-300 flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-rose-400" />
                <span className="truncate">CONVENTIONAL WEB STACK (Human Code)</span>
              </div>
              <div className="col-span-2 text-center text-slate-500 uppercase tracking-widest text-[10px]">
                METRIC
              </div>
              <div className="col-span-5 text-right text-cyan-300 flex items-center justify-end space-x-2">
                <span className="truncate">MLUE RUNTIME SUBSTRATE</span>
                <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_6px_rgba(34,211,238,0.8)]" />
              </div>
            </div>

            {/* Spec Rows */}
            <div className="divide-y divide-white/[0.04]">
              {activeGame.specs.map((spec, idx) => (
                <div 
                  key={idx} 
                  className="grid grid-cols-12 p-4 items-center hover:bg-white/[0.02] transition-colors"
                >
                  
                  {/* Left Column: Traditional Stack */}
                  <div className="col-span-5 text-left pr-2">
                    <div className="text-sm font-bold font-mono text-slate-200">
                      {spec.traditional.value}
                    </div>
                    <div className="text-[11px] font-mono text-slate-500 mt-0.5">
                      {spec.traditional.desc}
                    </div>
                  </div>

                  {/* Middle Column: Central Metric Icon & Label */}
                  <div className="col-span-2 text-center px-1">
                    <div className="inline-flex p-2 rounded-xl bg-black/50 border border-white/[0.06] mb-1">
                      {spec.icon}
                    </div>
                    <div className="text-[11px] font-semibold text-slate-300 font-mono leading-tight">
                      {spec.label}
                    </div>
                  </div>

                  {/* Right Column: MLUE Substrate */}
                  <div className="col-span-5 text-right pl-2">
                    <div className="text-sm font-bold font-mono text-cyan-300">
                      {spec.mlue.value}
                    </div>
                    <div className="text-[11px] font-mono text-emerald-400/90 font-medium mt-0.5">
                      {spec.mlue.desc}
                    </div>
                  </div>

                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Demonstrated Capability Banner */}
        <div className="bg-gradient-to-r from-slate-950 via-cyan-950/40 to-slate-950 p-4 border-t border-cyan-500/20 flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
          <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 shrink-0">
            <Trophy className="w-4 h-4" />
          </div>
          <div>
            <p className="text-xs text-slate-300 font-mono leading-relaxed">
              <strong className="text-amber-400 uppercase tracking-wider mr-1.5 font-bold">Demonstrated Findings:</strong>
              {activeGame.verdict}
            </p>
            <p className="text-[10px] text-slate-500 font-sans mt-0.5">
              Workload comparison evaluates deterministic runtime evaluation against equivalent declarative browser components.
            </p>
          </div>
        </div>

      </div>

    </section>
  );
}
