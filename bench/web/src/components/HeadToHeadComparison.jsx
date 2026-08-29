import React, { useState } from 'react';
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

export default function HeadToHeadComparison() {
  const [selectedGame, setSelectedGame] = useState('dashboard');

  const gamesData = {
    dashboard: {
      name: 'Interactive Dashboard',
      icon: '📊',
      verdict: 'Traditional stacks require 450 lines of React/Electron/Redux boilerplate and 500MB RAM. MLUE declares the complete data model, layout, and alarm rules in 1 unified JSON file.',
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
          traditional: { value: 'Runtime State Crashes', desc: 'Undefined prop & null pointer errors' },
          mlue: { value: '100% Statically Verified', desc: 'Mathematical reachability enforcement' }
        },
        {
          label: 'AI Introspection',
          sublabel: 'How AI agents inspect & mutate',
          icon: <Lock className="w-4 h-4 text-emerald-400" />,
          traditional: { value: 'Fragile DOM Scraping', desc: 'Breaks with every CSS change' },
          mlue: { value: 'Native MCP Protocol', desc: 'Deterministic JSON-RPC tools' }
        }
      ]
    },
    pong: {
      name: 'Pong',
      icon: '🏓',
      verdict: 'Traditional engines require 140 lines of manual code for a slower game. MLUE lets AI build a 10.7x faster, zero-glitch game with 0 code.',
      specs: [
        {
          label: 'Human Coding Effort',
          sublabel: 'Code required to build it',
          icon: <Code className="w-4 h-4 text-cyan-400" />,
          traditional: { value: '140 Lines', desc: 'Complex procedural code' },
          mlue: { value: '0 Lines', desc: 'AI builds it in 1 prompt' }
        },
        {
          label: 'Simulation Speed',
          sublabel: 'Physics execution speed',
          icon: <Zap className="w-4 h-4 text-amber-400" />,
          traditional: { value: '3,500 ticks/s', desc: 'Occasional frame drops' },
          mlue: { value: '37,400 ticks/s', desc: '10.7x Faster (Ultra Smooth)' }
        },
        {
          label: 'Memory Waste',
          sublabel: 'Memory garbage created',
          icon: <Trash2 className="w-4 h-4 text-rose-400" />,
          traditional: { value: '12,400 B/s', desc: 'Causes lag spikes & heat' },
          mlue: { value: '0.72 B/tick', desc: '99.9% Cleaner (0 Stutter)' }
        },
        {
          label: 'Screen Adaptation',
          sublabel: 'Watch, Mobile, 4K TV',
          icon: <Maximize2 className="w-4 h-4 text-teal-400" />,
          traditional: { value: 'Breaks on Resize', desc: 'Hardcoded pixel coordinates' },
          mlue: { value: '>16 Decades', desc: 'Pixel-perfect on all screens' }
        },
        {
          label: 'Bug & Glitch Rate',
          sublabel: 'Clipping & tunneling bugs',
          icon: <ShieldAlert className="w-4 h-4 text-indigo-400" />,
          traditional: { value: 'Frequent Tunneling', desc: 'Fast balls clip through walls' },
          mlue: { value: '0.00% Defect', desc: 'Mathematically proven physics' }
        },
        {
          label: 'Replay Determinism',
          sublabel: 'Cross-platform reliability',
          icon: <Lock className="w-4 h-4 text-emerald-400" />,
          traditional: { value: 'Non-Deterministic', desc: 'Diverges if CPU lags' },
          mlue: { value: '100% Bit-Exact', desc: 'SHA-256 Cryptographic Match' }
        }
      ]
    },
    breakout: {
      name: 'Breakout',
      icon: '🧱',
      verdict: 'Traditional Breakout needs complex brick-array loops and custom memory cleanup. MLUE declares 10 bricks in plain JSON with 0 tunneling defects.',
      specs: [
        {
          label: 'Human Coding Effort',
          sublabel: 'Code required to build it',
          icon: <Code className="w-4 h-4 text-cyan-400" />,
          traditional: { value: '260 Lines', desc: 'Manual brick arrays & loops' },
          mlue: { value: '0 Lines', desc: 'Declarative JSON rules only' }
        },
        {
          label: 'High-Speed Physics',
          sublabel: 'Fast ball collision integrity',
          icon: <Zap className="w-4 h-4 text-amber-400" />,
          traditional: { value: 'Glitches Through Bricks', desc: 'Fails under high velocity' },
          mlue: { value: 'v_max = 2.5 (10x Speed)', desc: 'Zero collision tunneling' }
        },
        {
          label: 'State Safety',
          sublabel: 'Runtime crash prevention',
          icon: <ShieldAlert className="w-4 h-4 text-indigo-400" />,
          traditional: { value: 'Runtime Crashes', desc: 'Fails on out-of-bounds bricks' },
          mlue: { value: '100% Statically Blocked', desc: 'Verified before execution' }
        },
        {
          label: 'Code Complexity',
          sublabel: 'Spaghetti logic score',
          icon: <Layers className="w-4 h-4 text-purple-400" />,
          traditional: { value: 'CC = 48 (High)', desc: 'Tangled nested if-else webs' },
          mlue: { value: 'CC = 21 (Bounded)', desc: 'Clean, modular math blocks' }
        },
        {
          label: 'Memory Waste',
          sublabel: 'Destroyed brick allocations',
          icon: <Trash2 className="w-4 h-4 text-rose-400" />,
          traditional: { value: '~18 KB/s Churn', desc: 'Garbage collector pauses' },
          mlue: { value: '< 1 B/tick', desc: 'Zero allocation overhead' }
        }
      ]
    },
    particles: {
      name: 'Physical Simulation',
      icon: '⚛️',
      verdict: 'Traditional particle sims suffer from energy leakage and frame drops. MLUE maintains exact mathematical energy conservation down to parts-per-billion.',
      specs: [
        {
          label: 'Energy Conservation',
          sublabel: 'Physical realism & drift',
          icon: <Zap className="w-4 h-4 text-amber-400" />,
          traditional: { value: 'Energy Leaks / Drift', desc: 'Particles slow down or explode' },
          mlue: { value: '0.0 PPB Drift', desc: 'Exact conservation across 1,000 hits' }
        },
        {
          label: 'OS Decoupling',
          sublabel: 'Runs without window system',
          icon: <Layers className="w-4 h-4 text-cyan-400" />,
          traditional: { value: 'Tied to Window Driver', desc: 'Requires Pygame/DirectX/OS' },
          mlue: { value: 'Tier L1 Substrate', desc: '0 foreign OS/GUI imports' }
        },
        {
          label: 'Simulation Speed',
          sublabel: 'Multi-entity throughput',
          icon: <Sparkles className="w-4 h-4 text-sand-400" />,
          traditional: { value: '~2,800 ticks/s', desc: 'Drops with more particles' },
          mlue: { value: '>30,000 ticks/s', desc: 'Ultra-fast vector physics' }
        },
        {
          label: 'Cross-Platform Portability',
          sublabel: 'Porting to C / Rust / Silicon',
          icon: <Maximize2 className="w-4 h-4 text-teal-400" />,
          traditional: { value: 'Requires Full Rewrite', desc: 'Code trapped in Python' },
          mlue: { value: '100% Substrate Decoupled', desc: 'Math runs anywhere unchanged' }
        }
      ]
    },
    inventory: {
      name: 'Hierarchical State Database',
      icon: '🎒',
      verdict: 'Traditional stacks require SQL databases, ORMs, table schemas, and serialization layers. MLUE manages nested lists, items, and crafting rules with 0 SQL and 0 ORM overhead.',
      specs: [
        {
          label: 'Database / ORM Overhead',
          sublabel: 'Storage & query layer',
          icon: <Code className="w-4 h-4 text-cyan-400" />,
          traditional: { value: 'SQL + Prisma / SQLAlchemy', desc: 'Complex migrations & table joins' },
          mlue: { value: '0 SQL / 0 ORM', desc: 'Hierarchical in-memory state tree' }
        },
        {
          label: 'Mutation Latency',
          sublabel: 'Time to push/pop/update state',
          icon: <Zap className="w-4 h-4 text-amber-400" />,
          traditional: { value: '2ms – 15ms (DB Query)', desc: 'Network & SQL parsing latency' },
          mlue: { value: '< 1 µs (Direct)', desc: 'Zero-overhead keypath mutation' }
        },
        {
          label: 'Data Integrity',
          sublabel: 'Static path & type verification',
          icon: <ShieldAlert className="w-4 h-4 text-indigo-400" />,
          traditional: { value: 'Runtime Schema Mismatches', desc: 'Broken foreign keys & nulls' },
          mlue: { value: '100% Statically Verified', desc: 'Compile-time path reachability' }
        },
        {
          label: 'Deterministic Rollouts',
          sublabel: 'State replay & rollback fidelity',
          icon: <Lock className="w-4 h-4 text-emerald-400" />,
          traditional: { value: 'Complex DB Snapshots', desc: 'Non-deterministic rollbacks' },
          mlue: { value: 'Bit-Exact SHA-256', desc: 'Cryptographic match on 50k steps' }
        }
      ]
    }
  };

  const activeGame = gamesData[selectedGame];

  return (
    <section className="mt-8 mb-12">
      
      {/* Header & Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-sm font-semibold tracking-tight text-white font-mono uppercase">
              Head-to-Head Architecture Comparison
            </h2>
            <span className="text-[10px] font-mono text-sand-400 px-2 py-0.5 rounded-full bg-sand-950/60 border border-sand-800/40 font-bold">
              REAL HARDWARE DATA
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-mono mt-0.5">
            How traditional human-centric software and game loops compare directly against the MLUE declarative substrate.
          </p>
        </div>

        {/* Game Selector Pills */}
        <div className="flex items-center gap-1.5 bg-black/40 p-1 rounded-xl border border-white/[0.06] text-xs font-mono">
          {Object.keys(gamesData).map((key) => {
            const g = gamesData[key];
            const isSelected = selectedGame === key;
            return (
              <button
                key={key}
                onClick={() => setSelectedGame(key)}
                className={`px-3 py-1.5 rounded-lg transition-all flex items-center space-x-1.5 ${
                  isSelected
                    ? 'bg-cyan-500 text-[#030712] font-bold shadow-sm shadow-cyan-500/20'
                    : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
                }`}
              >
                <span>{g.icon}</span>
                <span>{g.name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Comparison Spec Card (Mobile Spec Sheet Style) */}
      <div className="rounded-2xl apple-glass border border-white/[0.08] overflow-hidden shadow-2xl">
        
        {/* Table Column Headers */}
        <div className="grid grid-cols-12 bg-black/40 border-b border-white/[0.06] p-4 text-xs font-mono font-bold tracking-wider">
          <div className="col-span-5 text-left text-rose-300 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-rose-400" />
            <span className="truncate">TRADITIONAL STACK (Human Scaffolding)</span>
          </div>
          <div className="col-span-2 text-center text-slate-500 uppercase tracking-widest text-[10px]">
            METRIC
          </div>
          <div className="col-span-5 text-right text-cyan-300 flex items-center justify-end space-x-2">
            <span className="truncate">MLUE SUBSTRATE</span>
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
                <div className="inline-flex p-2 rounded-lg bg-black/50 border border-white/[0.06] mb-1">
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

        {/* Bottom Verdict Banner */}
        <div className="bg-gradient-to-r from-ocean-950 via-cyan-950/40 to-ocean-950 p-4 border-t border-cyan-500/20 flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-sand-500/10 border border-sand-500/30 text-sand-400">
            <Trophy className="w-4 h-4" />
          </div>
          <p className="text-xs text-slate-300 font-mono leading-relaxed">
            <strong className="text-sand-400 uppercase tracking-wider mr-1.5 font-bold">The Verdict:</strong>
            {activeGame.verdict}
          </p>
        </div>

      </div>

    </section>
  );
}
