import React from 'react';
import { Pill, Sunrise, Sun, Sunset, Moon, Clock, Utensils, AlertCircle, Check, ShieldCheck } from 'lucide-react';

export function MedicationTimingMatrix({ medications = [] }) {
  if (!medications || medications.length === 0) {
    return (
      <div className="bg-cream-50 rounded-2xl border border-cream-300 p-8 text-center">
        <Pill className="w-8 h-8 text-zinc-400 mx-auto mb-2" />
        <h4 className="text-sm font-bold text-zinc-700">No Prescribed Medications Detected</h4>
        <p className="text-xs text-zinc-500 mt-1">This document does not contain handwritten doctor prescription orders.</p>
      </div>
    );
  }

  const renderTimingSlot = (active, label) => {
    const isSlotActive = Boolean(active);
    return (
      <div className="flex flex-col items-center">
        <div
          className={`w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs transition-all ${
            isSlotActive
              ? 'bg-emerald-500 text-white shadow-sm ring-2 ring-emerald-300/60 scale-105'
              : 'bg-zinc-100 text-zinc-300'
          }`}
          title={`${label}: ${isSlotActive ? (typeof active === 'string' ? active : '1 Dose') : 'None'}`}
        >
          {isSlotActive ? (typeof active === 'string' || typeof active === 'number' ? active : '✓') : '—'}
        </div>
        <span className="text-[10px] text-zinc-400 font-medium mt-1">{label}</span>
      </div>
    );
  };

  return (
    <div className="bg-cream-50 rounded-2xl border border-cream-300 p-6 sm:p-8 shadow-soft">
      
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-cream-200">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1 rounded-md bg-emerald-100 text-emerald-800">
              <Pill className="w-4 h-4" />
            </span>
            <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider">
              Doctor Prescription Schedule
            </span>
          </div>
          <h3 className="text-xl sm:text-2xl font-black text-zinc-900 tracking-tight mt-0.5">
            Handwritten Drug Directions & Timing Matrix
          </h3>
          <p className="text-xs text-zinc-500 mt-1">
            transcription of shorthand notation (1-0-1, OD, BD, TDS, HS) mapped row-by-row.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs bg-white px-3 py-1.5 rounded-xl border border-cream-300 shadow-sm text-zinc-600">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>Cross-referenced Medical Nomenclature</span>
        </div>
      </div>

      {/* Responsive Table / Card Layout */}
      <div className="mt-6 overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-cream-300 text-[11px] font-bold text-zinc-500 uppercase tracking-wider">
              <th className="py-3 px-4">Medication & Strength</th>
              <th className="py-3 px-4 text-center">
                <span className="inline-flex items-center gap-1">
                  <Sunrise className="w-3.5 h-3.5 text-amber-500" /> Morning
                </span>
              </th>
              <th className="py-3 px-4 text-center">
                <span className="inline-flex items-center gap-1">
                  <Sun className="w-3.5 h-3.5 text-amber-600" /> Afternoon
                </span>
              </th>
              <th className="py-3 px-4 text-center">
                <span className="inline-flex items-center gap-1">
                  <Sunset className="w-3.5 h-3.5 text-orange-500" /> Evening
                </span>
              </th>
              <th className="py-3 px-4 text-center">
                <span className="inline-flex items-center gap-1">
                  <Moon className="w-3.5 h-3.5 text-indigo-500" /> Night
                </span>
              </th>
              <th className="py-3 px-4">Food Relation</th>
              <th className="py-3 px-4">Duration</th>
              <th className="py-3 px-4">Clinical Instructions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-cream-200 text-xs">
            {medications.map((med, index) => {
              const timing = med.timing || {};
              return (
                <tr key={index} className="hover:bg-medyellow-50/40 transition-colors">
                  
                  {/* Medication Details */}
                  <td className="py-4 px-4 align-top">
                    <div className="font-extrabold text-zinc-900 text-sm">
                      {med.drug_name}
                    </div>
                    {med.generic_name && (
                      <div className="text-[11px] text-zinc-500 italic mt-0.5">
                        ({med.generic_name})
                      </div>
                    )}
                    <div className="flex items-center gap-2 mt-1">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-zinc-100 text-zinc-700 border border-zinc-200">
                        {med.form || "Tablet"}
                      </span>
                      {med.dosage && (
                        <span className="text-[11px] font-mono font-bold text-emerald-800">
                          {med.dosage}
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Timing Matrix Slots */}
                  <td className="py-4 px-3 text-center align-middle">
                    {renderTimingSlot(timing.morning, 'Morn')}
                  </td>
                  <td className="py-4 px-3 text-center align-middle">
                    {renderTimingSlot(timing.afternoon, 'Aft')}
                  </td>
                  <td className="py-4 px-3 text-center align-middle">
                    {renderTimingSlot(timing.evening, 'Eve')}
                  </td>
                  <td className="py-4 px-3 text-center align-middle">
                    {renderTimingSlot(timing.night, 'Night')}
                  </td>

                  {/* Food Relation */}
                  <td className="py-4 px-4 align-top">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold ${
                      med.food_relation?.toLowerCase().includes('empty')
                        ? 'bg-amber-100 text-amber-900 border border-amber-200'
                        : med.food_relation?.toLowerCase().includes('before')
                        ? 'bg-blue-100 text-blue-900 border border-blue-200'
                        : 'bg-emerald-100 text-emerald-900 border border-emerald-200'
                    }`}>
                      <Utensils className="w-3 h-3" />
                      {med.food_relation || "After Food"}
                    </span>
                  </td>

                  {/* Duration */}
                  <td className="py-4 px-4 align-top">
                    <div className="font-semibold text-zinc-800 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-zinc-400" />
                      <span>{med.duration || "As advised"}</span>
                    </div>
                  </td>

                  {/* Instructions */}
                  <td className="py-4 px-4 align-top max-w-xs">
                    <p className="text-zinc-600 leading-relaxed text-[11px]">
                      {med.instructions || "Follow standard clinical dosing instructions."}
                    </p>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

