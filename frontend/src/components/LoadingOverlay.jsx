import React from 'react';
import { Activity, Sparkles, Brain, Clock } from 'lucide-react';

export function LoadingOverlay({ isVisible, message }) {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-zinc-950/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl border border-cream-300 text-center animate-in zoom-in-95 duration-200">
        
        {/* Animated medical pulse icon */}
        <div className="relative w-20 h-20 mx-auto mb-6">
          <div className="absolute inset-0 rounded-2xl bg-emerald-400 animate-ping opacity-25"></div>
          <div className="relative w-20 h-20 rounded-2xl bg-gradient-to-tr from-clinical-green to-emerald-600 flex items-center justify-center text-white shadow-lg shadow-emerald-500/30">
            <Activity className="w-10 h-10 animate-pulse stroke-[2.5]" />
          </div>
        </div>

        <h3 className="text-xl font-black text-zinc-900 tracking-tight">
          Qwen2.5-VL Vision Reasoning in Progress
        </h3>
        
        <p className="text-xs text-zinc-600 mt-2 leading-relaxed">
          {message || "Self-analyzing messy handwritten dosages, cross-referencing pharmaceutical dictionaries, and evaluating lab test boundaries..."}
        </p>

        {/* Progress step indicators */}
        <div className="mt-6 bg-cream-50 p-4 rounded-2xl border border-cream-200 text-left space-y-2.5">
          <div className="flex items-center gap-2.5 text-xs text-zinc-700 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>handwriting deciphering (1-0-1, OD, BD)</span>
          </div>
          <div className="flex items-center gap-2.5 text-xs text-zinc-700 font-medium">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
            <span>Parsing multi-table diagnostic lab metrics</span>
          </div>
          <div className="flex items-center gap-2.5 text-xs text-zinc-700 font-medium">
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
            <span>Isolating numeric out-of-safe-bound anomalies</span>
          </div>
        </div>

        <div className="mt-4 flex items-center justify-center gap-1.5 text-[11px] text-zinc-400">
          <Clock className="w-3.5 h-3.5" />
          <span>Typically takes 5-15s on T4 GPU</span>
        </div>
      </div>
    </div>
  );
}

