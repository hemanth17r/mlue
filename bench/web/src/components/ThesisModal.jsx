import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, BookOpen, ShieldCheck, Zap, Cpu, Sparkles, CheckCircle2 } from 'lucide-react';
import { backdropVariants, modalVariants, tapScale } from '../lib/motion';

export default function ThesisModal({ isOpen, onClose }) {
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      document.body.style.overflow = originalOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const pillars = [
    {
      icon: Cpu,
      title: 'The AI-Native Inversion',
      subtitle: 'AI is the builder. Humans are users.',
      desc: 'Conventional software stacks (DOM, Chromium, dynamic JS runtimes) are optimized for human developers typing manual code with high cognitive tolerance for runtime exceptions, CSS layout shifts, and heavy OS abstractions. MLUE inverts this: a compact, declarative, mathematical substrate designed specifically for generative models with zero dependencies and memory-mapped state.',
      color: 'text-cyan-400',
      bg: 'bg-cyan-950/30 border-cyan-500/20',
    },
    {
      icon: Zap,
      title: 'Microsecond Stepping & Symplectic Physics',
      subtitle: 'Sub-100 microsecond deterministic evaluation.',
      desc: 'By eliminating garbage-collected heap allocations and rendering layers from the critical path, MLUE steps simulations in microseconds. Symplectic numerical integration conserves total kinetic energy down to parts-per-billion, preventing numerical drift or explosions in long-horizon agent rollouts.',
      color: 'text-amber-400',
      bg: 'bg-amber-950/30 border-amber-500/20',
    },
    {
      icon: ShieldCheck,
      title: 'Mathematical Invariance & Static Safety',
      subtitle: 'Compile-time defect elimination before execution.',
      desc: 'Simulation coordinates are normalized in [0, 1] with >16 decades of IEEE 754 precision, guaranteeing absolute viewport invariance across watch to 8K displays. Hoare-logic reachability proves boundary safety before execution, eliminating unhandled runtime crashes entirely.',
      color: 'text-emerald-400',
      bg: 'bg-emerald-950/30 border-emerald-500/20',
    },
    {
      icon: Sparkles,
      title: 'In-Flight Agent Mutation via MCP',
      subtitle: 'Surgical live updates without execution stoppage.',
      desc: 'AI agents inspect and mutate active runtime state via deterministic Model Context Protocol (MCP) tools in sub-50 microseconds. State changes are atomic, verified, and instantly reflected in the running simulation without restarting the process.',
      color: 'text-indigo-400',
      bg: 'bg-indigo-950/30 border-indigo-500/20',
    },
  ];

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
        {/* Backdrop */}
        <motion.div
          {...backdropVariants}
          onClick={onClose}
          className="fixed inset-0 bg-black/80 backdrop-blur-md"
        />

        {/* Modal Dialog */}
        <motion.div
          {...modalVariants}
          className="relative w-full max-w-3xl bg-[#060D1A] border border-cyan-500/30 rounded-3xl shadow-2xl shadow-cyan-950/50 overflow-hidden my-auto z-10 flex flex-col max-h-[90vh]"
        >
          {/* Header */}
          <div className="p-5 sm:p-6 border-b border-white/[0.08] flex items-center justify-between bg-black/40">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                <BookOpen className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base sm:text-lg font-bold text-white font-mono tracking-tight">
                  MLUE Architecture Thesis
                </h2>
                <p className="text-xs text-cyan-400/90 font-mono">
                  Foundational Principles for the AI-Native Execution Substrate
                </p>
              </div>
            </div>

            <motion.button
              {...tapScale.button}
              type="button"
              onClick={onClose}
              className="p-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] text-slate-400 hover:text-white transition cursor-pointer border border-white/[0.06]"
            >
              <X className="w-4 h-4" />
            </motion.button>
          </div>

          {/* Body Content */}
          <div className="p-5 sm:p-6 overflow-y-auto space-y-5 font-sans">
            {/* Core Tenet Banner */}
            <div className="p-4 rounded-2xl bg-gradient-to-r from-cyan-950/50 via-slate-900 to-blue-950/40 border border-cyan-500/20 text-center">
              <div className="text-[11px] font-mono uppercase text-cyan-400 tracking-widest font-semibold mb-1">
                Core Substrate Tenet
              </div>
              <p className="text-sm sm:text-base text-white font-semibold leading-relaxed">
                "AI is the builder. Humans are users. Software substrates must be designed for generative synthesis, mathematical invariance, and compile-time boundary safety."
              </p>
            </div>

            {/* 4 Architectural Pillars */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              {pillars.map((p, idx) => {
                const Icon = p.icon;
                return (
                  <div
                    key={idx}
                    className={`p-4 rounded-2xl border ${p.bg} flex flex-col justify-between`}
                  >
                    <div>
                      <div className="flex items-center space-x-2 mb-2">
                        <Icon className={`w-4 h-4 ${p.color}`} />
                        <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider">
                          {p.title}
                        </h3>
                      </div>
                      <div className="text-[11px] font-semibold text-slate-300 mb-1.5 font-mono">
                        {p.subtitle}
                      </div>
                      <p className="text-[11px] text-slate-400 leading-relaxed font-sans">
                        {p.desc}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Empirical Grounding Note */}
            <div className="p-3.5 rounded-2xl bg-black/50 border border-white/[0.06] text-xs font-mono text-slate-400 flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Continuously Verified by Self-Contained Benchmark Harness</span>
              </span>
              <span className="text-[10px] text-slate-500">IEEE 754 • DO-178C • ISO 26262</span>
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-white/[0.08] bg-black/40 flex justify-end">
            <motion.button
              {...tapScale.button}
              type="button"
              onClick={onClose}
              className="px-5 py-1.5 rounded-full bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-mono text-xs font-bold transition cursor-pointer shadow-md shadow-cyan-500/20"
            >
              Close
            </motion.button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
