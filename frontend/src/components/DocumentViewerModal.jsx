import React from 'react';
import { Eye, X, ZoomIn, Download, FileText } from 'lucide-react';

export function DocumentViewerModal({ isOpen, onClose, file, previewUrl }) {
  if (!isOpen || !file) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 sm:p-6 animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl max-w-4xl w-full h-[85vh] flex flex-col shadow-2xl overflow-hidden border border-cream-300">
        
        {/* Modal Header */}
        <div className="px-6 py-4 bg-cream-50 border-b border-cream-200 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Eye className="w-5 h-5 text-emerald-600" />
            <div>
              <h3 className="text-sm font-bold text-zinc-900 truncate max-w-sm sm:max-w-md">
                {file.name}
              </h3>
              <p className="text-[11px] text-zinc-500">
                Original Uploaded Clinical Document
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg bg-zinc-100 hover:bg-zinc-200 text-zinc-700 flex items-center justify-center transition font-bold"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 bg-zinc-950/5 p-6 overflow-auto flex items-center justify-center">
          {previewUrl ? (
            <img
              src={previewUrl}
              alt="Medical Document Preview"
              className="max-h-full max-w-full object-contain rounded-lg shadow-lg border border-cream-200"
            />
          ) : (
            <div className="text-center p-8 bg-white rounded-2xl border border-cream-300 shadow-sm max-w-sm">
              <FileText className="w-16 h-16 text-red-500 mx-auto mb-3" />
              <h4 className="font-bold text-zinc-900 text-sm">PDF Document Rendered</h4>
              <p className="text-xs text-zinc-500 mt-1">
                This PDF has been rasterized into high-resolution pages for zero-shot clinical recognition.
              </p>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-cream-50 border-t border-cream-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-xs font-bold bg-clinical-black text-white hover:bg-clinical-black-hover transition"
          >
            Close Viewer
          </button>
        </div>
      </div>
    </div>
  );
}

