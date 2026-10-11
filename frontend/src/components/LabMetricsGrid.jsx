import React, { useState } from 'react';
import { Activity, AlertTriangle, ArrowUp, ArrowDown, CheckCircle2, ShieldAlert, Filter, Info } from 'lucide-react';

export function LabMetricsGrid({ metrics = [] }) {
  const [filterMode, setFilterMode] = useState('all'); // 'all', 'out_of_range', 'normal'
  const [categoryFilter, setCategoryFilter] = useState('ALL');

  if (!metrics || metrics.length === 0) {
    return (
      <div className="bg-cream-50 rounded-2xl border border-cream-300 p-8 text-center">
        <Activity className="w-8 h-8 text-zinc-400 mx-auto mb-2" />
        <h4 className="text-sm font-bold text-zinc-700">No Laboratory Metrics Detected</h4>
        <p className="text-xs text-zinc-500 mt-1">This document appears to be purely a prescription without diagnostic blood lab tables.</p>
      </div>
    );
  }

  const outOfRangeCount = metrics.filter(m => m.is_out_of_range).length;
  const normalCount = metrics.length - outOfRangeCount;

  // Extract categories
  const categories = ['ALL', ...new Set(metrics.map(m => m.category).filter(Boolean))];

  const filteredMetrics = metrics.filter(item => {
    if (filterMode === 'out_of_range' && !item.is_out_of_range) return false;
    if (filterMode === 'normal' && item.is_out_of_range) return false;
    if (categoryFilter !== 'ALL' && item.category !== categoryFilter) return false;
    return true;
  });

  return (
    <div className="bg-cream-50 rounded-2xl border border-cream-300 p-6 sm:p-8 shadow-soft">
      
      {/* Header & Filter Controls */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 pb-6 border-b border-cream-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-rose-500 animate-ping"></span>
            <span className="text-xs font-bold text-rose-800 uppercase tracking-wider">
              Diagnostic Laboratory Analysis
            </span>
          </div>
          <h3 className="text-xl sm:text-2xl font-black text-zinc-900 tracking-tight mt-0.5">
            Biochemical & Clinical Markers
          </h3>
          <p className="text-xs text-zinc-500 mt-1">
            Zero-shot numeric isolation cross-referenced against standard clinical safe ranges.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setFilterMode('all')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition ${
              filterMode === 'all'
                ? 'bg-zinc-900 text-white shadow-sm'
                : 'bg-white text-zinc-600 border border-cream-300 hover:bg-cream-100'
            }`}
          >
            All Tests ({metrics.length})
          </button>

          {/* Out-of-Range Tab (Highlighted in vibrant red) */}
          <button
            onClick={() => setFilterMode('out_of_range')}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition ${
              filterMode === 'out_of_range'
                ? 'bg-rose-600 text-white shadow-alert'
                : 'bg-rose-50 text-rose-800 border border-rose-300 hover:bg-rose-100'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Out-of-Range ({outOfRangeCount})</span>
          </button>

          <button
            onClick={() => setFilterMode('normal')}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition ${
              filterMode === 'normal'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'bg-emerald-50 text-emerald-800 border border-emerald-300 hover:bg-emerald-100'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Normal ({normalCount})</span>
          </button>
        </div>
      </div>

      {/* Category selection */}
      {categories.length > 2 && (
        <div className="flex items-center gap-2 overflow-x-auto py-3 no-scrollbar border-b border-cream-100">
          <span className="text-[11px] font-semibold text-zinc-400 uppercase shrink-0">Category:</span>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-medium whitespace-nowrap transition ${
                categoryFilter === cat
                  ? 'bg-medyellow-200 text-yellow-950 font-bold border border-yellow-400'
                  : 'bg-white/80 text-zinc-600 border border-cream-200 hover:bg-cream-100'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* Grid of Lab Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 mt-6">
        {filteredMetrics.map((item, idx) => {
          const isCritical = item.is_out_of_range;
          const isHigh = item.status?.includes('HIGH');
          const isLow = item.status?.includes('LOW');

          return (
            <div
              key={idx}
              className={`relative rounded-2xl p-5 transition-all duration-200 flex flex-col justify-between ${
                isCritical
                  ? 'bg-red-50/90 border-2 border-red-500 shadow-alert hover:scale-[1.01]'
                  : 'bg-white border border-cream-300 hover:border-cream-400 shadow-sm'
              }`}
            >
              {/* Card Header */}
              <div>
                <div className="flex items-start justify-between gap-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-zinc-400">
                    {item.category || "Biochemistry"}
                  </span>

                  {/* Status Badge */}
                  {isCritical ? (
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-black bg-red-600 text-white shadow-sm animate-pulse">
                      {isHigh ? <ArrowUp className="w-3 h-3 stroke-[3]" /> : <ArrowDown className="w-3 h-3 stroke-[3]" />}
                      {item.status?.replace('_', ' ') || 'OUT OF RANGE'}
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800">
                      <CheckCircle2 className="w-3 h-3" />
                      NORMAL
                    </span>
                  )}
                </div>

                {/* Test Name */}
                <h4 className={`text-base font-extrabold mt-1 leading-snug ${isCritical ? 'text-red-950' : 'text-zinc-900'}`}>
                  {item.test_name}
                </h4>

                {/* Observed Value Callout */}
                <div className="mt-4 flex items-baseline gap-2">
                  <span className={`text-3xl font-black tracking-tight font-mono ${
                    isCritical ? 'text-red-600' : 'text-emerald-700'
                  }`}>
                    {item.observed_value}
                  </span>
                  <span className={`text-sm font-semibold ${isCritical ? 'text-red-800' : 'text-zinc-500'}`}>
                    {item.unit}
                  </span>
                </div>
              </div>

              {/* Bottom Reference Boundaries & Notes */}
              <div className="mt-5 pt-3 border-t border-dashed border-zinc-200/80">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-zinc-500 font-medium">Safe Interval:</span>
                  <span className={`font-mono font-bold ${isCritical ? 'text-zinc-800' : 'text-zinc-700'}`}>
                    {item.reference_interval?.text || `${item.reference_interval?.min || ''} - ${item.reference_interval?.max || ''} ${item.unit}`}
                  </span>
                </div>

                {/* Clinical Significance Note if provided */}
                {item.clinical_significance && (
                  <div className={`mt-2.5 p-2 rounded-lg text-[11px] leading-relaxed flex items-start gap-1.5 ${
                    isCritical ? 'bg-red-100/80 text-red-900 font-medium' : 'bg-cream-100 text-zinc-600'
                  }`}>
                    <Info className="w-3.5 h-3.5 shrink-0 mt-0.5 text-zinc-500" />
                    <span>{item.clinical_significance}</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

