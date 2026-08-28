import React, { useState } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import HeadToHeadComparison from './components/HeadToHeadComparison';
import BenchmarkCard from './components/BenchmarkCard';
import VerificationTerminal from './components/VerificationTerminal';

// Real verified telemetry data from runs.json
import telemetryData from './telemetry.json';

export default function App() {
  const runs = Array.isArray(telemetryData) ? telemetryData : [telemetryData];
  const latestRun = runs[runs.length - 1] || null;
  const benchmarks = latestRun?.benchmarks || [];

  const [selectedCategory, setSelectedCategory] = useState('All');
  const categories = ['All', 'Architecture', 'Performance', 'Engineering', 'Physics', 'Verification'];

  const filteredBenchmarks = selectedCategory === 'All'
    ? benchmarks
    : benchmarks.filter(b => b.category.toLowerCase() === selectedCategory.toLowerCase());

  return (
    <div className="min-h-screen beach-radial-bg text-slate-100 flex flex-col justify-between selection:bg-cyan-500 selection:text-black">
      
      <div>
        {/* Navigation Header */}
        <Header latestRun={latestRun} />

        {/* Content Container */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
          
          {/* Keynote Style Hero */}
          <Hero latestRun={latestRun} />

          {/* E-Commerce Spec Style Head-to-Head Comparison */}
          <HeadToHeadComparison />

          {/* Section Divider & Filter Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mt-12 mb-6 border-t border-white/[0.06] pt-8">
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-semibold tracking-tight text-white font-mono uppercase">
                The 10 Invariant Matrix
              </h2>
              <span className="text-[11px] font-mono text-cyan-400/80 px-2 py-0.5 rounded-full bg-cyan-950/60 border border-cyan-800/40">
                100% EMPIRICAL
              </span>
            </div>

            {/* Filter Pills */}
            <div className="flex flex-wrap items-center gap-1 bg-black/40 p-1 rounded-xl border border-white/[0.06] text-[11px] font-mono">
              {categories.map(cat => (
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

          {/* 10 Benchmark Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredBenchmarks.map(benchmark => (
              <BenchmarkCard key={benchmark.id} benchmark={benchmark} />
            ))}
          </div>

          {/* Verification Drawer */}
          <VerificationTerminal />

        </main>
      </div>

      {/* Clean Footer */}
      <footer className="border-t border-white/[0.06] bg-black/30 backdrop-blur-xl py-6 mt-16 text-[11px] text-slate-500 font-mono text-center">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className="text-slate-300 font-semibold">MLUE Substrate</span>
            <span>•</span>
            <span>Phase 0.6 Capstone</span>
          </div>
          <span className="apple-ocean-text font-semibold">"AI is the builder. Humans are users."</span>
          <div className="text-slate-400">
            Audit Hash: <code className="text-cyan-300">{latestRun?.run_id || 'RUN_20260828'}</code>
          </div>
        </div>
      </footer>

    </div>
  );
}
