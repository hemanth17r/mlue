import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Copy, Check } from 'lucide-react';
import { tapScale } from '../lib/motion';

export default function VerificationTerminal() {
  const [copied, setCopied] = useState(false);
  const command = 'python bench/harness/runner.py';

  const handleCopy = () => {
    navigator.clipboard.writeText(command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="mt-10 p-5 rounded-2xl bg-slate-900/80 border border-white/[0.08] flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl">
      
      {/* Left: Info */}
      <div className="flex items-center space-x-3">
        <div className="p-2.5 rounded-xl bg-black/50 border border-cyan-500/20 text-cyan-400">
          <Terminal className="w-4 h-4" />
        </div>
        <div>
          <h4 className="text-xs font-bold text-white font-mono">Independent Local Hardware Audit</h4>
          <p className="text-[11px] text-slate-400 font-sans mt-0.5">Execute the self-verifying benchmark harness directly on your machine.</p>
        </div>
      </div>

      {/* Right: Clean Terminal Command Box (Inner element: rounded-xl, Button: rounded-full) */}
      <div className="flex items-center bg-black/75 border border-cyan-900/40 rounded-xl px-4 py-2 font-mono text-xs shadow-inner">
        <span className="text-cyan-400 mr-2.5 font-bold">$</span>
        <code className="text-slate-200 pr-4 select-all text-xs">{command}</code>
        <motion.button
          {...tapScale.button}
          onClick={handleCopy}
          className="px-3.5 py-1.5 rounded-full bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-black transition-all text-xs flex items-center gap-1.5 shadow-md shadow-cyan-500/20 cursor-pointer"
        >
          {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? 'Copied!' : 'Copy'}</span>
        </motion.button>
      </div>

    </section>
  );
}
