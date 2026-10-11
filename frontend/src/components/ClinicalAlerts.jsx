import React from 'react';
import { ShieldAlert, AlertTriangle, Info, BellRing } from 'lucide-react';

export function ClinicalAlerts({ alerts = [] }) {
  if (!alerts || alerts.length === 0) return null;

  return (
    <div className="bg-gradient-to-r from-rose-50 via-red-50 to-amber-50 rounded-2xl border-2 border-red-300 p-6 shadow-alert animate-in fade-in duration-300">
      <div className="flex items-center gap-3 pb-3 border-b border-red-200">
        <div className="w-10 h-10 rounded-xl bg-red-600 text-white flex items-center justify-center shadow-md">
          <ShieldAlert className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <h3 className="text-base font-black text-red-950 tracking-tight">
            Critical Clinical Alerts & Out-of-Bound Anomaly Tags
          </h3>
          <p className="text-xs text-red-800">
            Automated boundary rule safety checks isolated the following high-risk findings:
          </p>
        </div>
      </div>

      <div className="mt-4 space-y-2.5">
        {alerts.map((alert, index) => (
          <div
            key={index}
            className="flex items-start gap-3 p-3.5 rounded-xl bg-white/90 border border-red-200 text-xs shadow-sm"
          >
            <AlertTriangle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
            <div className="text-red-950 font-semibold leading-relaxed">
              {alert}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

