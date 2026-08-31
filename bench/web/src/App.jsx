import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Header from './components/Header';
import Hero from './components/Hero';
import Playground from './components/Playground';
import RunComparisonInspector from './components/RunComparisonInspector';
import HeadToHeadComparison from './components/HeadToHeadComparison';
import BenchmarkCard from './components/BenchmarkCard';
import VerificationTerminal from './components/VerificationTerminal';
import { springJelly, tapScale } from './lib/motion';

// Bundled telemetry snapshot for 0ms initial load
import initialTelemetry from './telemetry.json';

export default function App() {
  const [runs, setRuns] = useState(() =>
    Array.isArray(initialTelemetry) ? initialTelemetry : [initialTelemetry]
  );
  const [selectedRunIdx, setSelectedRunIdx] = useState(() => runs.length - 1);
  const [compareRunIdx, setCompareRunIdx] = useState(0);
  const [compareMode, setCompareMode] = useState('target'); // 'target' | 'previous' | 'baseline' | 'custom'
  const [selectedCategory, setSelectedCategory] = useState('All');

  // Determine initial view based on domain / hash
  const [activeView, setActiveView] = useState(() => {
    if (typeof window !== 'undefined') {
      if (window.location.hash === '#benchmarks' || window.location.hostname.includes('mlue-bench')) {
        return 'benchmarks';
      }
    }
    return 'studio';
  });

  const handleSelectView = (view) => {
    setActiveView(view);
    if (typeof window !== 'undefined') {
      window.location.hash = view === 'benchmarks' ? '#benchmarks' : '#studio';
    }
  };

  // Background GitHub Sync for real-time freshness
  useEffect(() => {
    const fetchLatestGitHubTelemetry = async () => {
      try {
        const res = await fetch(
          'https://raw.githubusercontent.com/hemanth17r/mlue/main/bench/telemetry/runs.json',
          { cache: 'no-store' }
        );
        if (res.ok) {
          const remoteRuns = await res.json();
          if (Array.isArray(remoteRuns) && remoteRuns.length >= runs.length) {
            setRuns(remoteRuns);
            setSelectedRunIdx(remoteRuns.length - 1);
          }
        }
      } catch {
        // Silently preserve local bundled data if offline or rate-limited
      }
    };

    fetchLatestGitHubTelemetry();
  }, []);

  const currentRun = runs[selectedRunIdx] || runs[runs.length - 1];
  const benchmarks = currentRun?.benchmarks || [];

  const categories = ['All', 'Architecture', 'Performance', 'Engineering', 'Physics', 'Verification'];

  const filteredBenchmarks =
    selectedCategory === 'All'
      ? benchmarks
      : benchmarks.filter((b) => b.category.toLowerCase() === selectedCategory.toLowerCase());

  return (
    <div className="min-h-screen beach-radial-bg text-slate-100 flex flex-col justify-between selection:bg-cyan-400 selection:text-black">
      <div>
        {/* Navigation Header */}
        <Header 
          latestRun={currentRun} 
          activeView={activeView}
          onSelectView={handleSelectView}
        />

        {/* Content Container */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10">
          
          {/* VIEW 1: DEDICATED AI STUDIO */}
          {activeView === 'studio' && (
            <div className="space-y-8">
              <Playground onOpenBenchmarks={() => handleSelectView('benchmarks')} />
            </div>
          )}

          {/* VIEW 2: 12 INVARIANT BENCHMARK MATRIX */}
          {activeView === 'benchmarks' && (
            <div className="space-y-12">
              {/* Keynote Style Hero */}
              <Hero latestRun={currentRun} />

              {/* Historical Run Comparison Inspector & Executive Synthesis */}
              <RunComparisonInspector
                runs={runs}
                selectedRunIdx={selectedRunIdx}
                onSelectRun={(idx) => setSelectedRunIdx(idx)}
                compareRunIdx={compareRunIdx}
                onSelectCompareRun={(idx) => setCompareRunIdx(idx)}
                compareMode={compareMode}
                setCompareMode={setCompareMode}
              />

              {/* Section Divider & Filter Bar */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-8 mb-6 border-t border-white/[0.06] pt-6">
                <div className="flex items-center space-x-2">
                  <h2 className="text-sm font-semibold tracking-tight text-white font-mono uppercase">
                    The {benchmarks.length} Invariant Matrix
                  </h2>
                  <span className="text-[11px] font-mono text-cyan-400/80 px-2.5 py-0.5 rounded-full bg-cyan-950/60 border border-cyan-800/40 font-semibold">
                    100% EMPIRICAL
                  </span>
                </div>

                {/* Filter Pills (Golden Standard: Floating Capsule Pill Tabs) */}
                <div className="flex flex-wrap items-center gap-1 bg-black/60 p-1 rounded-full border border-white/[0.08] shadow-inner font-mono text-xs relative">
                  {categories.map((cat) => {
                    const isActive = selectedCategory === cat;
                    return (
                      <motion.button
                        {...tapScale.pill}
                        key={cat}
                        onClick={() => setSelectedCategory(cat)}
                        className={`relative z-10 px-3.5 py-1.5 rounded-full transition-colors cursor-pointer text-xs font-bold ${
                          isActive ? 'text-slate-950 font-black' : 'text-slate-400 hover:text-white'
                        }`}
                      >
                        {isActive && (
                          <motion.div
                            layoutId="activeCategoryPill"
                            className="absolute inset-0 bg-cyan-400 rounded-full shadow-md shadow-cyan-500/20 z-[-1]"
                            transition={springJelly}
                          />
                        )}
                        {cat}
                      </motion.button>
                    );
                  })}
                </div>
              </div>

              {/* Invariant Benchmark Cards Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {filteredBenchmarks.map((benchmark) => (
                  <BenchmarkCard
                    key={benchmark.id}
                    benchmark={benchmark}
                    allRuns={runs}
                    currentRunIdx={selectedRunIdx}
                    compareRunIdx={compareRunIdx}
                    compareMode={compareMode}
                  />
                ))}
              </div>

              {/* Application Architecture Showcase (Head-to-Head Proofs) */}
              <div className="mt-14 pt-8 border-t border-white/[0.06]">
                <HeadToHeadComparison />
              </div>

              {/* Verification Terminal */}
              <VerificationTerminal />
            </div>
          )}

        </main>
      </div>

      {/* Clean Footer (Golden Standard) */}
      <footer className="border-t border-white/[0.06] bg-black/40 backdrop-blur-xl py-6 mt-16 text-xs text-slate-400 font-mono text-center">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className="text-slate-200 font-bold">MLUE Substrate</span>
            <span>•</span>
            <span className="text-cyan-400">{currentRun?.mlue_phase || 'Phase 1.6'}</span>
          </div>
          <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent font-bold">
            "AI is the builder. Humans are users."
          </span>
          <div className="text-slate-400">
            Audit Hash: <code className="text-cyan-300 font-semibold">{currentRun?.run_id || 'RUN_20260829'}</code>
          </div>
        </div>
      </footer>
    </div>
  );
}
