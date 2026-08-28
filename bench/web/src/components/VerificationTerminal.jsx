import React, { useState } from 'react';
import { Terminal, Copy, Check } from 'lucide-react';

export default function VerificationTerminal() {
  const [copied, setCopied] = useState(false);
  const command = 'python bench/harness/runner.py';

  const handleCopy = () => {
    navigator.clipboard.writeText(command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="mt-10 p-5 rounded-2xl apple-glass flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      
      {/* Left: Info */}
      <div className="flex items-center space-x-3">
        <div className="p-2 rounded-xl bg-black/40 border border-cyan-500/20">
          <Terminal className="w-4 h-4 text-cyan-400" />
        </div>
        <div>
          <h4 className="text-xs font-semibold text-white font-mono">Independent Hardware Verification</h4>
          <p className="text-[11px] text-slate-400 font-mono">Execute the self-auditing benchmark harness on your local machine.</p>
        </div>
      </div>

      {/* Right: Clean Terminal Command Box */}
      <div className="flex items-center bg-black/60 border border-cyan-900/30 rounded-xl px-3.5 py-1.5 font-mono text-xs shadow-inner">
        <span className="text-cyan-400 mr-2 font-bold">$</span>
        <code className="text-slate-200 pr-4 select-all text-[11px]">{command}</code>
        <button
          onClick={handleCopy}
          className="px-2.5 py-1 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-[#030712] font-bold transition-all text-[11px] flex items-center gap-1 shadow-sm shadow-cyan-500/20 active:scale-95"
        >
          {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>

    </section>
  );
}
