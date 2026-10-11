import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { FileUploader } from './components/FileUploader';
import { PatientOverview } from './components/PatientOverview';
import { LabMetricsGrid } from './components/LabMetricsGrid';
import { MedicationTimingMatrix } from './components/MedicationTimingMatrix';
import { ClinicalAlerts } from './components/ClinicalAlerts';
import { DocumentViewerModal } from './components/DocumentViewerModal';
import { LoadingOverlay } from './components/LoadingOverlay';
import { analyzeDocument, checkColabStatus, fetchSampleData } from './services/api';
import { Eye, Code, FileText, CheckCircle2, AlertTriangle, ArrowRight, Sparkles } from 'lucide-react';

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [showDocModal, setShowDocModal] = useState(false);
  const [showRawJson, setShowRawJson] = useState(false);
  const [colabStatus, setColabStatus] = useState(null);
  const [customColabUrl, setCustomColabUrl] = useState(() => {
    const saved = localStorage.getItem('colab_url');
    if (saved && !saved.includes('your-colab-tunnel') && saved.startsWith('http')) {
      return saved;
    }
    return '';
  });

  // Check Colab connection on mount
  useEffect(() => {
    handleCheckStatus();
  }, [customColabUrl]);

  const handleCheckStatus = async () => {
    try {
      const res = await checkColabStatus(customColabUrl);
      setColabStatus(res);
    } catch (err) {
      setColabStatus({
        status: 'offline',
        accessible: false,
        message: 'Backend server reachable; Colab tunnel offline.'
      });
    }
  };

  const handleUpdateColabUrl = (newUrl) => {
    setCustomColabUrl(newUrl);
    localStorage.setItem('colab_url', newUrl);
  };

  const handleFileSelected = (file) => {
    setSelectedFile(file);
    setError(null);
    if (file.type.startsWith('image/')) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    setAnalysisResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setError(null);

    try {
      const result = await analyzeDocument(selectedFile, customColabUrl);
      setAnalysisResult(result);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to analyze document.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleLoadSample = async () => {
    setIsAnalyzing(true);
    setError(null);
    try {
      const sample = await fetchSampleData();
      setAnalysisResult(sample);
      // Create a virtual file indicator for sample
      setSelectedFile({
        name: 'verified_prescription_lab_composite.jpg',
        size: 3450000,
        type: 'image/jpeg'
      });
    } catch (err) {
      console.error(err);
      setError('Could not load sample data from backend.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-cream-100 text-zinc-900 flex flex-col font-sans">
      
      {/* Top Application Header */}
      <Header
        colabStatus={colabStatus}
        onRefreshStatus={handleCheckStatus}
        customColabUrl={customColabUrl}
        onUpdateColabUrl={handleUpdateColabUrl}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Error notification banner */}
        {error && (
          <div className="bg-rose-50 border-2 border-rose-300 rounded-2xl p-4 flex items-start gap-3 shadow-sm animate-in fade-in">
            <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div className="flex-1 text-xs">
              <strong className="font-bold text-rose-900 block text-sm">Clinical Pipeline Notice</strong>
              <p className="text-rose-800 mt-0.5">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-rose-400 hover:text-rose-600 font-bold"
            >
              ✕
            </button>
          </div>
        )}

        {/* Upload Card */}
        <section className="no-print">
          <FileUploader
            selectedFile={selectedFile}
            onFileSelected={handleFileSelected}
            onAnalyze={handleAnalyze}
            onReset={handleReset}
            isAnalyzing={isAnalyzing}
            onLoadSample={handleLoadSample}
          />
        </section>

        {/* Analysis Results Display */}
        {analysisResult && (
          <div className="space-y-8 print-page animate-in fade-in slide-in-from-bottom-4 duration-300">
            
            {/* Top Toolbar for Results */}
            <div className="flex flex-wrap items-center justify-between gap-4 bg-medyellow-50/80 border border-medyellow-200 p-4 rounded-2xl no-print">
              <div className="flex items-center gap-3">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <span className="text-xs font-bold text-zinc-800">
                  Zero-Shot Extraction Complete ({analysisResult.medications?.length || 0} Drugs • {analysisResult.lab_metrics?.length || 0} Lab Markers)
                </span>
                {analysisResult.metadata?.source === 'mock_fallback' && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-200 text-amber-900">
                    Offline Emulated Sample
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2.5">
                {selectedFile && (
                  <button
                    onClick={() => setShowDocModal(true)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-white border border-cream-300 text-zinc-700 hover:bg-cream-100 transition shadow-sm"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>View Uploaded Document</span>
                  </button>
                )}

                <button
                  onClick={() => setShowRawJson(!showRawJson)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-white border border-cream-300 text-zinc-700 hover:bg-cream-100 transition shadow-sm"
                >
                  <Code className="w-3.5 h-3.5" />
                  <span>{showRawJson ? 'Hide JSON' : 'Raw Model JSON'}</span>
                </button>
              </div>
            </div>

            {/* Raw JSON viewer */}
            {showRawJson && (
              <div className="bg-zinc-900 text-emerald-400 p-5 rounded-2xl text-xs font-mono overflow-auto max-h-96 border border-zinc-800 no-print">
                <pre>{JSON.stringify(analysisResult, null, 2)}</pre>
              </div>
            )}

            {/* 1. Critical Alerts & Out-of-Bounds Boundary Flags */}
            <ClinicalAlerts alerts={analysisResult.critical_alerts} />

            {/* 2. Patient & Attending Doctor Overview Card */}
            <PatientOverview data={analysisResult} onPrint={handlePrint} />

            {/* 3. High-Risk Out-of-Range Lab Metrics Grid (Vibrant Red) */}
            <LabMetricsGrid metrics={analysisResult.lab_metrics} />

            {/* 4. Handwritten Drug Directions & Timing Matrix (Row-by-Row) */}
            <MedicationTimingMatrix medications={analysisResult.medications} />

            {/* 5. Clinical Transcription Confidence Summary */}
            {analysisResult.transcription_confidence_summary && (
              <div className="bg-cream-50 rounded-2xl border border-cream-300 p-5 text-xs text-zinc-600 flex items-start gap-3 shadow-soft">
                <Sparkles className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-zinc-800 font-bold block mb-0.5">Model Zero-Shot Verification Summary</strong>
                  <p className="leading-relaxed">{analysisResult.transcription_confidence_summary}</p>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-cream-300 bg-cream-50 py-6 text-center text-xs text-zinc-500 no-print">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p>
            Project 2: Specialized Zero-Shot Medical Chart & Prescription Intelligence
          </p>
          <p className="text-[11px] text-zinc-400">
            Intended for clinical pair-programming, laboratory review, and decision assistance.
          </p>
        </div>
      </footer>

      {/* Document Viewer Modal */}
      <DocumentViewerModal
        isOpen={showDocModal}
        onClose={() => setShowDocModal(false)}
        file={selectedFile}
        previewUrl={previewUrl}
      />

      {/* Loading Overlay */}
      <LoadingOverlay isVisible={isAnalyzing} />
    </div>
  );
}

