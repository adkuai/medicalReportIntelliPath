import React, { useState } from 'react';
import { Activity, Cpu, Server, CheckCircle2, AlertCircle, RefreshCw, ExternalLink } from 'lucide-react';

export function Header({ colabStatus, onRefreshStatus, customColabUrl, onUpdateColabUrl }) {
  const [showUrlModal, setShowUrlModal] = useState(false);
  const [inputUrl, setInputUrl] = useState(customColabUrl || '');

  const handleSaveUrl = (e) => {
    e.preventDefault();
    onUpdateColabUrl(inputUrl);
    setShowUrlModal(false);
  };

  return (
    <header className="bg-cream-50/80 backdrop-blur-md border-b border-cream-300 sticky top-0 z-30 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        
        {/* Brand / Logo */}
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-clinical-green to-emerald-600 flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
            <Activity className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-lg sm:text-xl text-zinc-900 tracking-tight">
                medical <span className="text-emerald-700">Report</span> IntelliPath
              </h1>
              <span className="hidden md:inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-medyellow-100 text-yellow-900 border border-yellow-300">
                v1.0 Clinical
              </span>
            </div>
            <p className="text-xs text-zinc-500 flex items-center gap-2 mt-0.5">
              <span>Powered by <strong className="text-zinc-700">Qwen2.5-VL-7B-Instruct</strong></span>
              <span className="w-1 h-1 rounded-full bg-zinc-300"></span>
              <span>T4 GPU Acceleration</span>
            </p>
          </div>
        </div>

        {/* Status Indicators & Colab Tunnel Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowUrlModal(true)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
              colabStatus?.accessible
                ? 'bg-emerald-50 border-emerald-300 text-emerald-800 hover:bg-emerald-100'
                : 'bg-amber-50 border-amber-300 text-amber-900 hover:bg-amber-100'
            }`}
            title="Configure or test Google Colab ngrok tunnel"
          >
            <Server className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Colab AI Node:</span>
            <span className="flex items-center gap-1 font-semibold">
              <span className={`w-2 h-2 rounded-full ${colabStatus?.accessible ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`}></span>
              {colabStatus?.accessible ? 'Connected' : 'Offline / Emulated'}
            </span>
          </button>

          <button
            onClick={onRefreshStatus}
            className="p-2 rounded-lg border border-cream-300 bg-white hover:bg-cream-200 text-zinc-600 transition"
            title="Recheck connection status"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Modal to configure Colab Tunnel URL */}
      {showUrlModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-cream-300 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-cream-200">
              <div className="flex items-center gap-2 text-zinc-900 font-bold text-base">
                <Cpu className="w-5 h-5 text-emerald-600" />
                <span>Google Colab Tunnel Connection</span>
              </div>
              <button
                onClick={() => setShowUrlModal(false)}
                className="text-zinc-400 hover:text-zinc-600 font-bold text-lg"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveUrl} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-zinc-700 mb-1.5">
                  Public Colab ngrok URL
                </label>
                <input
                  type="url"
                  placeholder="https://xxxx-xx.ngrok-free.app"
                  value={inputUrl}
                  onChange={(e) => setInputUrl(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-zinc-300 bg-cream-50 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                />
                <p className="text-[11px] text-zinc-500 mt-1.5 leading-relaxed">
                  Paste the public URL printed at Step 5 in your Google Colab notebook. If empty or unreachable, the system automatically uses verified offline medical intelligence for demonstration.
                </p>
              </div>

              <div className="bg-cream-100 p-3 rounded-lg text-xs space-y-1.5 text-zinc-600">
                <div className="flex justify-between">
                  <span className="font-medium">Model:</span>
                  <span className="font-semibold text-zinc-800">Qwen2.5-VL-7B-Instruct (4-bit NF4)</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Target VRAM:</span>
                  <span className="font-semibold text-zinc-800">~6 GB / 15 GB (Free T4)</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Current Status:</span>
                  <span className={`font-semibold ${colabStatus?.accessible ? 'text-emerald-700' : 'text-amber-700'}`}>
                    {colabStatus?.accessible ? 'Online & Ready' : colabStatus?.message || 'Not Connected'}
                  </span>
                </div>
              </div>

              <div className="flex justify-end gap-2.5 pt-2">
                <button
                  type="button"
                  onClick={() => setShowUrlModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold bg-zinc-100 text-zinc-700 hover:bg-zinc-200 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600 text-white hover:bg-emerald-700 transition shadow-sm"
                >
                  Save & Connect
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </header>
  );
}

