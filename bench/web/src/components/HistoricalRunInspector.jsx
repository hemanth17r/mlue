import React from 'react';
import { History, Clock, CheckCircle2 } from 'lucide-react';

export default function HistoricalRunInspector({ runs, selectedRunIndex, onSelectRun }) {
  if (!runs || runs.length === 0) return null;

  const currentRun = runs[selectedRunIndex] || runs[runs.length - 1];

  return (
    <section className="mb-6 p-4 rounded-xl glass-card flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono">
      
      {/* Left: Metadata */}
      <div className="flex items-center space-x-3 text-slate-400">
        <div className="flex items-center space-x-1.5 text-cyan-400 font-semibold">
          <History className="w-3.5 h-3.5" />
          <span>Audit Log:</span>
        </div>
        <span className="text-slate-200 font-semibold">{currentRun.run_id}</span>
        <span className="text-slate-600">•</span>
        <span>{new Date(currentRun.timestamp).toUTCString()}</span>
      </div>

      {/* Right: Run Selector Pills */}
      {runs.length > 1 && (
        <div className="flex items-center gap-1.5 overflow-x-auto">
          {runs.map((run, idx) => {
            const isSelected = idx === selectedRunIndex;
            const dateObj = new Date(run.timestamp);
            const timeLabel = isNaN(dateObj.getTime())
              ? run.run_id
              : dateObj.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

            return (
              <button
                key={run.run_id}
                onClick={() => onSelectRun(idx)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-mono transition-all ${
                  isSelected
                    ? 'bg-cyan-500 text-ocean-950 font-bold shadow-sm shadow-cyan-500/20'
                    : 'bg-ocean-950 text-slate-400 hover:text-slate-200 hover:bg-ocean-900 border border-slate-800'
                }`}
              >
                {timeLabel} ({run.passed_count}/{run.total_count})
              </button>
            );
          })}
        </div>
      )}

    </section>
  );
}
