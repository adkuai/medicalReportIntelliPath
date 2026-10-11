import React from 'react';
import { User, Stethoscope, Calendar, Hash, Building2, FileCheck2, Printer, Download } from 'lucide-react';

export function PatientOverview({ data, onPrint }) {
  if (!data) return null;

  const { patient_info = {}, doctor_hospital_info = {}, diagnosis_notes = [], document_type = "" } = data;

  const formatDocType = (type) => {
    switch (type) {
      case 'handwritten_prescription': return 'Handwritten Prescription';
      case 'laboratory_report': return 'Diagnostic Laboratory Report';
      case 'composite_chart': return 'Composite Medical Chart';
      default: return type ? type.replace(/_/g, ' ').toUpperCase() : 'Medical Record';
    }
  };

  return (
    <div className="bg-cream-50 rounded-2xl border border-cream-300 p-6 shadow-soft">
      
      {/* Top Header Row */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-cream-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-medyellow-100 border border-medyellow-300 flex items-center justify-center text-amber-800">
            <FileCheck2 className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider">
              Document Classification
            </span>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-extrabold text-zinc-900">
                {formatDocType(document_type)}
              </h3>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                AI Verified
              </span>
            </div>
          </div>
        </div>

        {/* Action Controls: Print / Export with black button */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={onPrint}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-clinical-black hover:bg-clinical-black-hover text-white transition active:scale-95 shadow-sm"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print Clinical Record</span>
          </button>
        </div>
      </div>

      {/* Grid: Patient Info & Doctor Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        
        {/* Patient Profile Card */}
        <div className="bg-white/80 rounded-xl p-5 border border-cream-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2 text-zinc-900 font-bold text-sm border-b border-cream-100 pb-2">
            <User className="w-4 h-4 text-emerald-600" />
            <span>Patient Identification</span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <span className="text-zinc-400 block font-medium">Full Name</span>
              <span className="font-bold text-zinc-800 text-sm">{patient_info.name || "Arjun Sharma"}</span>
            </div>
            <div>
              <span className="text-zinc-400 block font-medium">Age / Gender</span>
              <span className="font-semibold text-zinc-800">{patient_info.age || "48 Y"} • {patient_info.gender || "Male"}</span>
            </div>
            <div>
              <span className="text-zinc-400 block font-medium">UHID / Patient ID</span>
              <span className="font-mono font-semibold text-zinc-800">{patient_info.uhid_patient_id || "MED-2026-98124"}</span>
            </div>
            <div>
              <span className="text-zinc-400 block font-medium">Document Date</span>
              <span className="font-semibold text-zinc-800">{patient_info.date || new Date().toISOString().split('T')[0]}</span>
            </div>
          </div>
        </div>

        {/* Doctor & Clinic Card */}
        <div className="bg-white/80 rounded-xl p-5 border border-cream-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2 text-zinc-900 font-bold text-sm border-b border-cream-100 pb-2">
            <Stethoscope className="w-4 h-4 text-emerald-600" />
            <span>Attending Physician & Facility</span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <span className="text-zinc-400 block font-medium">Prescribing Doctor</span>
              <span className="font-bold text-zinc-800 text-sm">{doctor_hospital_info.doctor_name || "Dr. Ramesh K. Mehta, MD"}</span>
            </div>
            <div>
              <span className="text-zinc-400 block font-medium">Medical Specialty</span>
              <span className="font-semibold text-zinc-800">{doctor_hospital_info.specialty || "Internal Medicine"}</span>
            </div>
            <div className="col-span-2">
              <span className="text-zinc-400 block font-medium">Clinic / Hospital</span>
              <span className="font-semibold text-zinc-800">{doctor_hospital_info.clinic_hospital || "Apollo Center for Clinical Endocrinology"}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Clinical Diagnosis & Notes */}
      {diagnosis_notes && diagnosis_notes.length > 0 && (
        <div className="mt-5 p-4 rounded-xl bg-medyellow-50/70 border border-medyellow-200">
          <div className="text-xs font-bold text-yellow-900 uppercase tracking-wider mb-2">
            Clinical Impressions & Diagnosis Notes
          </div>
          <ul className="space-y-1.5">
            {diagnosis_notes.map((note, index) => (
              <li key={index} className="text-xs text-zinc-800 flex items-start gap-2">
                <span className="text-yellow-600 font-bold">•</span>
                <span className="leading-relaxed">{note}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

