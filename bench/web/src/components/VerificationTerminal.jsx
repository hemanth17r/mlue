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
    <section className="mt-10 p-4 sm:p-5 rounded-2xl bg-slate-900/80 border border-white/[0.08] flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
      
      {/* Left: Info */}
      <div className="flex items-center space-x-3">
        <div className="p-2.5 rounded-xl bg-black/50 border border-cyan-500/20 text-cyan-400 shrink-0">
          <Terminal className="w-4 h-4" />
        </div>
        <h4 className="text-xs font-bold text-white font-mono">Local Execution</h4>
      </div>

      {/* Right: Clean Terminal Command Box */}
      <div className="flex items-center justify-between bg-black/75 border border-cyan-900/40 rounded-xl px-3 sm:px-4 py-2 font-mono text-xs shadow-inner w-full md:w-auto max-w-full gap-2">
        <div className="flex items-center truncate">
          <span className="text-cyan-400 mr-2 font-bold shrink-0">$</span>
          <code className="text-slate-200 select-all text-xs truncate">{command}</code>
        </div>
        <motion.button
          {...tapScale.button}
          type="button"
          aria-label="Copy command to clipboard"
          onClick={handleCopy}
          className="px-3 sm:px-3.5 py-1.5 rounded-full bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-black transition-all text-xs flex items-center gap-1.5 shadow-md shadow-cyan-500/20 cursor-pointer shrink-0 ml-2"
        >
          {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? 'Copied!' : 'Copy'}</span>
        </motion.button>
      </div>

    </section>
  );
}
