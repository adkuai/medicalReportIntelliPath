import React, { useRef, useState } from 'react';
import { UploadCloud, FileText, Image as ImageIcon, Trash2, Sparkles, Check, AlertCircle } from 'lucide-react';

export function FileUploader({ onFileSelected, onAnalyze, onReset, selectedFile, isAnalyzing, onLoadSample }) {
  const [dragActive, setDragActive] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file) => {
    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg', 'application/pdf'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(jpg|jpeg|png|webp|pdf)$/i)) {
      alert("Please upload a valid image (JPG, PNG, WEBP) or a PDF document.");
      return;
    }

    onFileSelected(file);

    if (file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null);
    }
  };

  const handleTriggerSelect = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleClear = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    onReset();
  };

  return (
    <div className="w-full bg-cream-50 rounded-2xl border border-cream-300 p-6 sm:p-8 shadow-soft">
      
      {/* Top Banner & Instructions */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-6 border-b border-cream-200">
        <div>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-medyellow-100 text-yellow-900 border border-medyellow-300 mb-2">
            <Sparkles className="w-3.5 h-3.5 text-yellow-700" />
            Document Extraction
          </span>
          <h2 className="text-xl sm:text-2xl font-black text-zinc-900 tracking-tight">
            Upload Prescription or Laboratory Report
          </h2>
          <p className="text-sm text-zinc-600 mt-1 max-w-2xl leading-relaxed">
            Upload high-resolution smartphone photographs of messy, handwritten doctor prescriptions or complex multi-page laboratory test reports.
          </p>
        </div>

        {/* Demo Sample button */}
        <button
          onClick={onLoadSample}
          disabled={isAnalyzing}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-medyellow-100 text-yellow-950 border border-yellow-300 hover:bg-medyellow-200 active:scale-95 transition shadow-sm"
        >
          <Sparkles className="w-4 h-4 text-amber-700" />
          Load Verified Demo Sample
        </button>
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,application/pdf"
        className="hidden"
        onChange={handleChange}
      />

      {/* Spaced Document Insertion Area */}
      <div className="mt-6">
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`relative rounded-2xl border-2 border-dashed p-8 sm:p-10 transition-all duration-200 flex flex-col items-center justify-center text-center ${
            dragActive
              ? 'border-clinical-green bg-emerald-50/50 scale-[1.005]'
              : selectedFile
              ? 'border-emerald-300 bg-medyellow-50/40'
              : 'border-cream-400 bg-cream-100/60 hover:bg-medyellow-50/30'
          }`}
        >
          {selectedFile ? (
            /* Selected File State */
            <div className="w-full flex flex-col sm:flex-row items-center justify-between gap-6">
              <div className="flex items-center gap-4 text-left">
                {previewUrl ? (
                  <div className="w-20 h-24 rounded-xl border-2 border-white shadow-md overflow-hidden bg-white shrink-0">
                    <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
                  </div>
                ) : (
                  <div className="w-20 h-24 rounded-xl bg-red-100 border border-red-200 flex flex-col items-center justify-center text-red-700 shadow-sm shrink-0">
                    <FileText className="w-8 h-8" />
                    <span className="text-[10px] font-bold mt-1 uppercase">PDF Doc</span>
                  </div>
                )}
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-base font-bold text-zinc-900 truncate max-w-xs sm:max-w-md">
                      {selectedFile.name}
                    </span>
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-100 text-emerald-800">
                      Ready
                    </span>
                  </div>
                  <p className="text-xs text-zinc-500 mt-1">
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • {selectedFile.type || "Medical Document"}
                  </p>
                  <p className="text-xs text-emerald-700 font-medium mt-1">
                    ✓ High resolution validated for Qwen2.5-VL clinical OCR
                  </p>
                </div>
              </div>

              {/* Action Buttons inside upload card */}
              <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
                {/* Black Button for Re-upload */}
                <button
                  type="button"
                  onClick={handleClear}
                  disabled={isAnalyzing}
                  className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-clinical-black hover:bg-clinical-black-hover text-white transition active:scale-95 shadow-md disabled:opacity-50"
                  title="Clear document and choose another"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Re-upload / Reset</span>
                </button>

                {/* Light Green Button to Run Extraction */}
                <button
                  type="button"
                  onClick={onAnalyze}
                  disabled={isAnalyzing}
                  className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl text-xs font-bold bg-clinical-green hover:bg-clinical-green-hover text-white transition active:scale-95 shadow-md shadow-emerald-500/20 disabled:opacity-50"
                >
                  <Sparkles className="w-4 h-4" />
                  <span>{isAnalyzing ? "Analyzing Document..." : "Analyze Clinical Chart"}</span>
                </button>
              </div>
            </div>
          ) : (
            /* Empty Insertion State */
            <div className="space-y-4 max-w-md">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-medyellow-100 border border-medyellow-300 flex items-center justify-center text-amber-700 shadow-sm">
                <UploadCloud className="w-8 h-8" />
              </div>

              <div>
                <h3 className="text-base font-bold text-zinc-800">
                  Drag and drop your medical file here
                </h3>
                <p className="text-xs text-zinc-500 mt-1">
                  Supports JPEG, PNG, WEBP high-res photos and multi-page PDF documents (Up to 25MB)
                </p>
              </div>

              {/* Prompt Buttons: Light Green Select Button & Black Reset Button */}
              <div className="flex items-center justify-center gap-3 pt-2">
                {/* Light Green Select Button */}
                <button
                  type="button"
                  onClick={handleTriggerSelect}
                  className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold bg-clinical-green hover:bg-clinical-green-hover text-white shadow-md shadow-emerald-500/20 active:scale-95 transition"
                >
                  <ImageIcon className="w-4 h-4" />
                  <span>Select Document</span>
                </button>

                {/* Black Button for Re-upload / Option */}
                <button
                  type="button"
                  onClick={handleTriggerSelect}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold bg-clinical-black hover:bg-clinical-black-hover text-white shadow-md active:scale-95 transition"
                >
                  <span>Re-upload Option</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Feature Pills */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-6 pt-4 border-t border-cream-200">
        <div className="flex items-center gap-2.5 text-xs text-zinc-600 bg-cream-100/80 p-2.5 rounded-xl border border-cream-300/60">
          <div className="w-2 h-2 rounded-full bg-emerald-500 shrink-0"></div>
          <span><strong>Messy Handwriting:</strong> Doctor dosage & shorthand transcription (1-0-1, OD, BD)</span>
        </div>
        <div className="flex items-center gap-2.5 text-xs text-zinc-600 bg-cream-100/80 p-2.5 rounded-xl border border-cream-300/60">
          <div className="w-2 h-2 rounded-full bg-rose-500 shrink-0"></div>
          <span><strong>Out-of-Range Isolation:</strong> Outlier lab metrics tagged in vibrant red cards</span>
        </div>
        <div className="flex items-center gap-2.5 text-xs text-zinc-600 bg-cream-100/80 p-2.5 rounded-xl border border-cream-300/60">
          <div className="w-2 h-2 rounded-full bg-amber-500 shrink-0"></div>
          <span><strong>Timing Matrix:</strong> Morning, afternoon, evening, night rows with meal relations</span>
        </div>
      </div>
    </div>
  );
}

