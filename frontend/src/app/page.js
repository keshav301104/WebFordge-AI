"use client";
import { useState, useEffect } from "react";
import { startGeneration, checkJobStatus } from "@/lib/api";
import VariantCard from "@/components/VariantCard";
import { Loader2, Zap, Globe, Image as ImageIcon, Sparkles, Hexagon, Settings2, Share2, Workflow, MessageSquareText } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function Dashboard() {
  const [url, setUrl] = useState("");
  const [adUrl, setAdUrl] = useState("");
  const [file, setFile] = useState(null);
  const [customPrompt, setCustomPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [jobStatus, setJobStatus] = useState(null);
  const [variants, setVariants] = useState([]);

  useEffect(() => {
    let interval;
    if (loading && jobStatus?.job_id && jobStatus?.status !== "completed") {
      interval = setInterval(async () => {
        try {
          const data = await checkJobStatus(jobStatus.job_id);
          setJobStatus(data);
          if (data.status === "completed") {
            setVariants(data.variants);
            setLoading(false);
          }
        } catch (err) { console.error(err); }
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [loading, jobStatus]);

  const handleRun = async (e) => {
    e.preventDefault();
    setLoading(true);
    setVariants([]);
    try {
      const data = await startGeneration(url, file, adUrl, customPrompt);
      setJobStatus({ job_id: data.job_id, status: "pending", current_step: "Initializing Quantum Engine..." });
    } catch (err) { 
      setLoading(false); 
      alert("Engine connection failed. Ensure backend is running.");
    }
  };

  return (
    <div className="app-container">
      <div className="mesh-bg" />

      {/* ========================================= */}
      {/* FIXED SIDEBAR */}
      {/* ========================================= */}
      <aside className="w-[380px] flex-shrink-0 bg-white/50 backdrop-blur-3xl border-r border-white p-8 flex flex-col z-[50] shadow-[10px_0_50px_-10px_rgba(0,0,0,0.03)] overflow-y-auto custom-scrollbar">
        
        <div className="flex items-center gap-4 mb-10 shrink-0">
          <div className="relative h-14 w-14 rounded-2xl p-[1px] bg-gradient-to-b from-slate-300 to-slate-100 shadow-lg shadow-slate-200/50">
            <div className="absolute inset-0 bg-slate-900 rounded-[15px] m-[1px] flex items-center justify-center">
               <Hexagon className="text-white" size={24} strokeWidth={2} />
            </div>
          </div>
          <div>
            <h1 className="text-xl font-black tracking-tight text-slate-900">
              WEBFORGE AI
            </h1>
            <div className="flex items-center gap-2 mt-0.5">
              <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.6)]" />
              <p className="text-[9px] font-bold text-slate-400 tracking-[0.2em] uppercase">Enterprise Agentic v1.0</p>
            </div>
          </div>
        </div>

        <div className="flex-grow flex flex-col">
          <h2 className="text-[10px] font-black text-slate-800 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
            <Settings2 size={14} className="text-slate-400"/> Engine Inputs
          </h2>
          
          <form onSubmit={handleRun} className="space-y-5">
            
            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-slate-400 uppercase tracking-widest ml-2">Landing Source</label>
              <div className="relative group">
                <Globe className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-indigo-500 transition-colors" size={16}/>
                <input 
                  className="w-full bg-white/80 border border-white focus:border-indigo-300 transition-all pl-11 pr-4 py-3.5 rounded-2xl text-xs font-medium shadow-sm outline-none backdrop-blur-md"
                  placeholder="https://client-demo.com"
                  value={url} onChange={(e) => setUrl(e.target.value)} required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-slate-400 uppercase tracking-widest ml-2">Creative Context</label>
              <div className="relative group mb-2">
                <ImageIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-indigo-500 transition-colors" size={16}/>
                <input 
                  className="w-full bg-white/80 border border-white focus:border-indigo-300 transition-all pl-11 pr-4 py-3.5 rounded-2xl text-xs font-medium shadow-sm outline-none backdrop-blur-md"
                  placeholder="Ad Image URL"
                  value={adUrl} onChange={(e) => setAdUrl(e.target.value)}
                />
              </div>
              <input type="file" onChange={(e) => setFile(e.target.files[0])} className="text-[10px] font-bold text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:bg-white file:shadow-sm file:text-indigo-600 hover:file:bg-indigo-50 transition-colors cursor-pointer w-full" />
            </div>

            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-slate-400 uppercase tracking-widest ml-2 flex items-center justify-between">
                 <span>Steering Prompt</span>
                 <span className="text-slate-300 font-medium normal-case tracking-normal">Optional</span>
              </label>
              <div className="relative group">
                <MessageSquareText className="absolute left-4 top-4 text-slate-400 group-focus-within:text-indigo-500 transition-colors" size={16}/>
                <textarea 
                  className="w-full bg-white/80 border border-white focus:border-indigo-300 transition-all pl-11 pr-4 py-3.5 rounded-2xl text-xs font-medium shadow-sm outline-none backdrop-blur-md resize-none h-20 custom-scrollbar leading-relaxed"
                  placeholder="e.g., Target Gen-Z. Make it aggressive..."
                  value={customPrompt} onChange={(e) => setCustomPrompt(e.target.value)}
                />
              </div>
            </div>

            {/* THE UPGRADED GLOWING BUTTON */}
            <button 
              disabled={loading} 
              className="relative group w-full py-4 rounded-2xl font-black text-[10px] uppercase tracking-[0.2em] transition-all active:scale-[0.98] overflow-hidden flex items-center justify-center text-white shadow-[0_10px_30px_-10px_rgba(99,102,241,0.6)] mt-4 border border-indigo-500/30"
            >
              {/* Vibrant Gradient Base */}
              <div className="absolute inset-0 bg-gradient-to-r from-violet-600 via-indigo-500 to-blue-500 group-hover:scale-[1.02] transition-transform duration-500" />
              {/* Hover Glow Shift */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-indigo-500 to-violet-600 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
              {/* Shimmer Sweep */}
              <div className="absolute inset-0 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite] bg-gradient-to-r from-transparent via-white/30 to-transparent" />
              
              <span className="relative z-10 flex items-center gap-2 drop-shadow-md">
                {loading ? <Loader2 className="animate-spin text-white" size={16}/> : <>Start Reconstruction <Workflow size={14}/></>}
              </span>
            </button>
          </form>
        </div>

        <div className="mt-6 pt-6 border-t border-white flex justify-between items-center opacity-60 shrink-0">
           <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">L4 Autonomy Level</span>
           <Share2 size={14} className="text-slate-400" />
        </div>
      </aside>

      {/* ========================================= */}
      {/* MAIN VIEWPORT */}
      {/* ========================================= */}
      <main className="flex-grow overflow-y-auto p-12 custom-scrollbar relative">
        <div className="max-w-[1400px] mx-auto h-full flex flex-col">
          <AnimatePresence mode="wait">
            
            {/* THE "GOD-LEVEL" TRANSITION STATE */}
            {loading ? (
              <motion.div 
                key="loading"
                initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
                className="flex-grow flex flex-col items-center justify-center min-h-[70vh]"
              >
                {/* The Quantum Core Visualization */}
                <div className="relative w-80 h-80 flex items-center justify-center mb-12">
                  
                  {/* Deep Core Glow */}
                  <div className="absolute inset-0 bg-gradient-to-tr from-violet-500/20 to-blue-500/20 blur-[100px] rounded-full animate-pulse" />
                  
                  {/* Outer Dashed Orbit */}
                  <motion.div 
                    animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 25, ease: "linear" }} 
                    className="absolute inset-0 border border-dashed border-slate-300 rounded-full opacity-40"
                  />
                  
                  {/* Mid Orbiting Particles */}
                  <motion.div animate={{ rotate: -360 }} transition={{ repeat: Infinity, duration: 12, ease: "linear" }} className="absolute inset-8 z-10">
                    <div className="absolute top-0 left-1/2 w-3 h-3 bg-indigo-500 rounded-full shadow-[0_0_20px_rgba(99,102,241,1)] -translate-x-1/2 -translate-y-1/2" />
                  </motion.div>
                  
                  {/* Inner Solid Tech Ring */}
                  <motion.div 
                    animate={{ rotate: 180 }} transition={{ repeat: Infinity, duration: 15, ease: "linear", repeatType: "mirror" }} 
                    className="absolute inset-16 border-[2px] border-transparent border-t-indigo-500 border-b-violet-500 rounded-full opacity-70"
                  />

                  {/* Inner Core Particle */}
                  <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 8, ease: "linear" }} className="absolute inset-20 z-10">
                    <div className="absolute bottom-0 left-1/2 w-2 h-2 bg-blue-400 rounded-full shadow-[0_0_15px_rgba(96,165,250,1)] -translate-x-1/2 translate-y-1/2" />
                  </motion.div>
                  
                  {/* The Hexagon Brain */}
                  <motion.div 
                    animate={{ scale: [1, 1.1, 1] }} transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
                    className="relative h-28 w-28 bg-white border border-slate-100 rounded-3xl shadow-2xl shadow-indigo-500/20 flex items-center justify-center z-20 overflow-hidden"
                  >
                    <div className="absolute inset-0 bg-gradient-to-tr from-indigo-50 to-white" />
                    <Hexagon className="text-indigo-600 relative z-10" size={48} strokeWidth={1.5} fill="rgba(99,102,241,0.05)"/>
                  </motion.div>
                </div>

                {/* The Sleek Status Text */}
                <div className="flex flex-col items-center">
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-3 px-5 py-2 rounded-full bg-slate-900 shadow-xl shadow-slate-900/20 mb-5 border border-slate-700"
                  >
                    <Sparkles size={14} className="text-indigo-400 animate-pulse"/>
                    <span className="text-[10px] font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-violet-400 uppercase tracking-[0.3em]">
                      Neural Engine Active
                    </span>
                  </motion.div>
                  
                  <h3 className="text-2xl font-black text-slate-800 tracking-tight text-center max-w-lg leading-snug">
                    {jobStatus?.current_step || "Synthesizing Domain Architecture..."}
                  </h3>
                </div>
              </motion.div>
            
            // Success State
            ) : variants.length > 0 ? (
              <motion.div 
                key="results"
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                className="grid grid-cols-1 2xl:grid-cols-2 gap-10"
              >
                {variants.map((v, i) => <VariantCard key={i} variant={v} originalUrl={url} />)}
              </motion.div>
            
            // Empty State
            ) : (
              <motion.div 
                key="empty"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="flex-grow flex flex-col items-center justify-center min-h-[70vh]"
              >
                <div className="h-20 w-20 bg-white border border-white rounded-[2rem] flex items-center justify-center text-slate-300 mb-6 shadow-sm hover:scale-105 transition-transform duration-500">
                  <Zap size={32} fill="currentColor" />
                </div>
                <h2 className="text-2xl font-black text-slate-400 uppercase tracking-[0.2em]">System Standby</h2>
                <p className="text-slate-500 mt-2 font-medium text-xs">Configure parameters to initiate generation.</p>
              </motion.div>
            )}
            
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}