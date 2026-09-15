import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import Hero from './components/Hero';
import RunComparisonInspector from './components/RunComparisonInspector';
import HeadToHeadComparison from './components/HeadToHeadComparison';
import BenchmarkCard from './components/BenchmarkCard';
import VerificationTerminal from './components/VerificationTerminal';
import ThesisModal from './components/ThesisModal';
import { springJelly, tapScale } from './lib/motion';

// Bundled telemetry snapshot for 0ms initial load
import initialTelemetry from './telemetry.json';

export default function App() {
  const [runs, setRuns] = useState(() =>
    Array.isArray(initialTelemetry) ? initialTelemetry : [initialTelemetry]
  );
  const [selectedRunIdx, setSelectedRunIdx] = useState(() => runs.length - 1);
  const [compareRunIdx, setCompareRunIdx] = useState(() => Math.max(0, runs.length - 2));
  const [compareMode, setCompareMode] = useState('target'); // 'target' | 'previous' | 'v25' | 'p16' | 'custom'
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [isThesisOpen, setIsThesisOpen] = useState(false);

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
          const localCount = runs.length;
          const localBenchCount = runs[runs.length - 1]?.benchmarks?.length || 15;
          const remoteLatestBenchCount = remoteRuns[remoteRuns.length - 1]?.benchmarks?.length || 0;

          if (
            Array.isArray(remoteRuns) &&
            remoteRuns.length >= localCount &&
            remoteLatestBenchCount >= localBenchCount
          ) {
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

  const getCategoryGroup = (b) => {
    if (!b) return 'Architecture';
    if (b.id === 'B12' || (b.category && b.category.includes('Portability'))) return 'Verification';
    if (b.id === 'B13' || (b.category && b.category.includes('RL'))) return 'Performance';
    return b.category || 'Architecture';
  };

  const categories = ['All', 'Architecture', 'Performance', 'Engineering', 'Physics', 'Verification'];

  const getCategoryCount = (cat) => {
    if (cat === 'All') return benchmarks.length;
    return benchmarks.filter((b) => getCategoryGroup(b).toLowerCase() === cat.toLowerCase()).length;
  };

  const filteredBenchmarks =
    selectedCategory === 'All'
      ? benchmarks
      : benchmarks.filter((b) => getCategoryGroup(b).toLowerCase() === selectedCategory.toLowerCase());

  return (
    <div className="min-h-screen beach-radial-bg text-slate-100 flex flex-col justify-between selection:bg-cyan-400 selection:text-black">
      <div>
        {/* Navigation Header */}
        <Header 
          latestRun={currentRun} 
          onOpenThesis={() => setIsThesisOpen(true)}
        />

        {/* Content Container: Real 15-Pillar Empirical Telemetry Suite */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10">
          <div className="space-y-12">
            {/* Keynote Style Hero (Direct punchy headline + 4 metric boxes) */}
            <Hero latestRun={currentRun} />

            {/* Historical Run Comparison Inspector */}
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
                <h2 className="text-sm font-bold tracking-tight text-white font-mono uppercase flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_6px_rgba(34,211,238,0.8)]" />
                  <span>Specifications</span>
                </h2>
              </div>

              {/* Filter Pills */}
              <div className="flex flex-wrap items-center gap-1 bg-black/60 p-1 rounded-2xl sm:rounded-full border border-white/[0.08] shadow-inner font-mono text-xs relative">
                {categories.map((cat) => {
                  const isActive = selectedCategory === cat;
                  const count = getCategoryCount(cat);
                  return (
                    <motion.button
                      {...tapScale.pill}
                      key={cat}
                      type="button"
                      aria-pressed={isActive}
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
                      {cat} ({count})
                    </motion.button>
                  );
                })}
              </div>
            </div>

            {/* Benchmark Cards Grid */}
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
        </main>
      </div>

      {/* Dedicated Architecture Thesis Modal */}
      <ThesisModal 
        isOpen={isThesisOpen} 
        onClose={() => setIsThesisOpen(false)} 
      />
    </div>
  );
}
