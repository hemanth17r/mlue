import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import RunComparisonInspector from './components/RunComparisonInspector';
import HeadToHeadComparison from './components/HeadToHeadComparison';
import BenchmarkCard from './components/BenchmarkCard';
import VerificationTerminal from './components/VerificationTerminal';

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
    <div className="min-h-screen beach-radial-bg text-slate-100 flex flex-col justify-between selection:bg-cyan-500 selection:text-black">
      <div>
        {/* Navigation Header */}
        <Header latestRun={currentRun} />

        {/* Content Container */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
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
              <span className="text-[11px] font-mono text-cyan-400/80 px-2 py-0.5 rounded-full bg-cyan-950/60 border border-cyan-800/40">
                100% EMPIRICAL
              </span>
            </div>

            {/* Filter Pills */}
            <div className="flex flex-wrap items-center gap-1 bg-black/40 p-1 rounded-xl border border-white/[0.06] text-[11px] font-mono">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1 rounded-lg transition-all ${
                    selectedCategory === cat
                      ? 'bg-cyan-500 text-[#030712] font-bold shadow-sm shadow-cyan-500/20'
                      : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
                  }`}
                >
                  {cat}
                </button>
              ))}
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
        </main>
      </div>

      {/* Clean Footer */}
      <footer className="border-t border-white/[0.06] bg-black/30 backdrop-blur-xl py-6 mt-16 text-[11px] text-slate-500 font-mono text-center">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className="text-slate-300 font-semibold">MLUE Substrate</span>
            <span>•</span>
            <span>{currentRun?.mlue_phase || 'Phase 1.6'}</span>
          </div>
          <span className="apple-ocean-text font-semibold">"AI is the builder. Humans are users."</span>
          <div className="text-slate-400">
            Audit Hash: <code className="text-cyan-300">{currentRun?.run_id || 'RUN_20260829'}</code>
          </div>
        </div>
      </footer>
    </div>
  );
}
