import React, { useState } from 'react';
import { Terminal, Copy, Check } from 'lucide-react';

export default function ReproduceSection() {
  const [copied, setCopied] = useState(false);
  const command = 'python bench/harness/runner.py';

  const handleCopy = () => {
    navigator.clipboard.writeText(command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="mt-10 p-5 rounded-2xl glass-card border border-cyan-900/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div className="flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-ocean-950 border border-sand-900/40">
          <Terminal className="w-4 h-4 text-sand-400" />
        </div>
        <div>
          <h4 className="text-xs font-bold text-white font-mono">Independent Verification</h4>
          <p className="text-[11px] text-slate-500 font-mono">Execute the self-auditing benchmark on your hardware.</p>
        </div>
      </div>

      <div className="flex items-center bg-ocean-950 border border-cyan-900/40 rounded-lg px-3 py-1.5 font-mono text-xs shadow-inner">
        <span className="text-cyan-400 mr-2">$</span>
        <code className="text-slate-200 pr-4 select-all">{command}</code>
        <button
          onClick={handleCopy}
          className="px-2.5 py-1 rounded bg-cyan-600 hover:bg-cyan-500 text-ocean-950 font-bold transition-all text-[11px] flex items-center gap-1 shadow-sm"
        >
          {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>
    </section>
  );
}
