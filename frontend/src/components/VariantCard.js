"use client";
import { useState } from "react";
import { ShieldCheck, Download, BarChart, Maximize2, X, ExternalLink } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function VariantCard({ variant, originalUrl }) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // 1. Intercept & Inject Base Tag
  let rawHtml = variant.html_content;
  if (originalUrl) {
    const baseUrl = originalUrl.endsWith('/') ? originalUrl : `${originalUrl}/`;
    if (rawHtml.toLowerCase().includes('<head>')) {
      rawHtml = rawHtml.replace(/<head>/i, `<head><base href="${baseUrl}">`);
    } else {
      rawHtml = `<base href="${baseUrl}">\n` + rawHtml;
    }
  }

  // 2. Create the secure Blob
  const blob = new Blob([rawHtml], { type: "text/html" });
  const iframeSrc = URL.createObjectURL(blob);

  // 3. Fix the Download Handler
  const downloadHtml = (e) => {
    e.stopPropagation(); // Stops the card from expanding when you click download
    const link = document.createElement("a");
    link.href = iframeSrc;
    link.download = `webforge_${variant.variant_name.toLowerCase()}_variant.html`;
    link.click();
  };

  return (
    <>
      {/* ========================================= */}
      {/* THUMBNAIL VIEW (Locked, no scroll, no lag) */}
      {/* ========================================= */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        onClick={() => setIsExpanded(true)}
        className="group bg-white rounded-[2.5rem] p-4 border border-slate-200/60 shadow-sm hover:shadow-2xl hover:shadow-indigo-500/10 transition-all duration-500 flex flex-col h-full cursor-pointer relative overflow-hidden"
      >
        <div className="absolute top-8 right-8 z-20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-slate-900/80 backdrop-blur-md text-white p-2 rounded-xl flex items-center gap-2 text-xs font-bold shadow-xl">
          <Maximize2 size={14} /> Expand View
        </div>

        <div className="relative aspect-[16/10] w-full rounded-[1.8rem] overflow-hidden bg-slate-50 border border-slate-100 mb-6">
          <iframe 
            src={iframeSrc} 
            className="w-full h-[140%] border-none pointer-events-none scale-[0.75] origin-top" 
            title={variant.variant_name} 
            tabIndex={-1}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-white/40 via-transparent to-transparent pointer-events-none" />
        </div>

        <div className="px-4 pb-2 mt-auto">
          <div className="flex justify-between items-start mb-4">
            <div>
              <span className="inline-block px-3 py-1 bg-indigo-50 text-indigo-600 text-[10px] font-bold rounded-full mb-2 uppercase tracking-tighter border border-indigo-100">
                {variant.variant_name} Path
              </span>
              <h3 className="text-xl font-black text-slate-900 leading-none group-hover:text-indigo-600 transition-colors">Reconstruction Alpha</h3>
            </div>
            
            <button 
              onClick={downloadHtml}
              className="h-10 w-10 flex items-center justify-center bg-slate-100 text-slate-600 rounded-2xl hover:bg-slate-900 hover:text-white transition-all shadow-sm z-10 relative"
              title="Download Variant"
            >
              <Download size={18} />
            </button>
          </div>

          <div className="flex items-center gap-6 border-t border-slate-100 pt-4 mt-2">
            <div className="flex items-center gap-2">
               <BarChart size={16} className="text-slate-400" />
               <span className="text-sm font-bold text-slate-700">
                 {variant.confidence_score}% <span className="text-[10px] text-slate-400 font-medium uppercase tracking-widest ml-1">Match</span>
               </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* ========================================= */}
      {/* EXPANDED MODAL VIEW (Interactive, scrollable) */}
      {/* ========================================= */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[999] bg-slate-900/60 backdrop-blur-xl flex items-center justify-center p-6 md:p-12"
            onClick={() => setIsExpanded(false)} // Click background to close
          >
            <motion.div 
              initial={{ scale: 0.95, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 20 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside the modal
              className="bg-white w-full max-w-7xl h-full max-h-[90vh] rounded-[2rem] shadow-2xl flex flex-col overflow-hidden border border-slate-200/50"
            >
              {/* Modal Header */}
              <div className="h-16 px-6 border-b border-slate-100 flex items-center justify-between bg-slate-50 shrink-0">
                <div className="flex items-center gap-4">
                  <div className="h-3 w-3 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                  <span className="font-bold text-slate-700 text-sm">{variant.variant_name} Strategy Preview</span>
                </div>
                <div className="flex items-center gap-3">
                  <button onClick={downloadHtml} className="flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-600 hover:bg-indigo-600 hover:text-white rounded-xl text-xs font-bold transition-colors">
                    <Download size={14} /> Export HTML
                  </button>
                  <button onClick={() => setIsExpanded(false)} className="p-2 bg-slate-200/50 hover:bg-slate-200 text-slate-500 rounded-xl transition-colors">
                    <X size={18} />
                  </button>
                </div>
              </div>

              {/* Modal Body - Fully Interactive Iframe */}
              <div className="flex-grow w-full bg-white relative">
                <iframe 
                  src={iframeSrc} 
                  className="w-full h-full border-none pointer-events-auto" 
                  title={`${variant.variant_name} Expanded`}
                />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}