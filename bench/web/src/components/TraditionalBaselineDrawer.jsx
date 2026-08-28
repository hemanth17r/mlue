import React, { useState } from 'react';
import { Scale, ChevronDown, ChevronUp } from 'lucide-react';

export default function TraditionalBaselineDrawer() {
  const [open, setOpen] = useState(false);

  const comparisonRows = [
    { trait: 'Paradigm', baseline: 'Procedural game loop', mlue: 'Declarative JSON (0 code)' },
    { trait: 'Bespoke SLOC', baseline: '120–250 lines/game', mlue: '0 lines (Universal primitives)' },
    { trait: 'Static Reachability', baseline: 'Unbounded crash space', mlue: '100% Compile-time verification' },
    { trait: 'Memory Churn', baseline: '~12 KB/s dynamic alloc', mlue: '0.72 B/tick steady-state' },
    { trait: 'Spatial Invariance', baseline: 'Broken on resize', mlue: '>16.0 Decades precision' },
    { trait: 'Determinism', baseline: 'Thread/timer sensitive', mlue: '100% Bit-exact SHA-256 match' },
  ];

  return (
    <section className="mb-6 rounded-xl glass-card border border-cyan-900/30 overflow-hidden">
      
      <button
        onClick={() => setOpen(!open)}
        className="w-full p-4 text-left flex items-center justify-between hover:bg-ocean-900/30 transition-colors"
      >
        <div className="flex items-center space-x-2.5">
          <Scale className="w-4 h-4 text-sand-400" />
          <span className="text-xs font-bold text-white tracking-tight font-mono">
            Traditional Stack (Pygame) vs. MLUE Substrate
          </span>
        </div>

        <div className="flex items-center space-x-1 text-[11px] font-mono text-cyan-400">
          <span>{open ? 'Collapse' : 'Compare'}</span>
          {open ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </button>

      {open && (
        <div className="p-4 pt-0 border-t border-cyan-900/20 overflow-x-auto">
          <table className="w-full text-left text-[11px] font-mono">
            <thead>
              <tr className="border-b border-cyan-900/30 text-slate-500">
                <th className="py-2 px-2">Trait</th>
                <th className="py-2 px-2">Traditional Baseline</th>
                <th className="py-2 px-2">MLUE Declarative</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyan-900/10">
              {comparisonRows.map((row, i) => (
                <tr key={i} className="hover:bg-ocean-900/20">
                  <td className="py-2 px-2 font-semibold text-slate-300">{row.trait}</td>
                  <td className="py-2 px-2 text-slate-500">{row.baseline}</td>
                  <td className="py-2 px-2 text-cyan-300 font-bold">{row.mlue}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

    </section>
  );
}
