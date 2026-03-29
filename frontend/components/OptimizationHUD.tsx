'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { usePrismStore } from '@/lib/store';
import { useState, useEffect } from 'react';

function TacticalBox({ title, children }: { title: string, children: React.ReactNode }) {
  return (
    <div className="glass-panel relative overflow-hidden mb-8 bg-black/60 backdrop-blur-3xl border border-cyan-500/20 group rounded-xl">
       {/* Background accent */}
       <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/[0.05] to-transparent pointer-events-none" />
       
       <div className="relative z-10 p-6">
         <div className="font-orbitron text-[11px] text-cyan-400 font-bold tracking-[5px] uppercase mb-6 flex items-center gap-4">
           <div className="w-6 h-px bg-cyan-400/40" />
           {title}
         </div>
         <div className="space-y-5">{children}</div>
       </div>

       {/* Industrial accents */}
       <div className="absolute top-0 left-0 w-4 h-px bg-cyan-400/60" />
       <div className="absolute top-0 left-0 h-4 w-px bg-cyan-400/60" />
       <div className="absolute bottom-0 right-0 w-4 h-px bg-cyan-400/30" />
       <div className="absolute bottom-0 right-0 h-4 w-px bg-cyan-400/30" />
    </div>
  );
}

function DataRow({ label, value, color = "rgba(255,255,255,1)" }: { label: string, value: string, color?: string }) {
  return (
    <div className="flex justify-between items-baseline group py-3 border-b border-white/[0.05] last:border-0 hover:bg-white/[0.03] transition-colors px-2 -mx-2 rounded-lg">
       <span className="font-mono-tech text-[10px] text-white/50 tracking-[2px] uppercase truncate mr-6">{label}</span>
       <span className="font-orbitron font-extrabold tracking-tight text-[15px] truncate max-w-[180px]" style={{ color }}>{value}</span>
    </div>
  );
}

export default function OptimizationHUD() {
  const { showOptimizationResults, selectedCountry, scanResult, isScanning, resetScan, setShowOptimizationResults, missionMode } = usePrismStore();
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let interval: any;
    if (isScanning) {
      setProgress(0);
      interval = setInterval(() => {
        setProgress(p => p < 100 ? p + Math.random() * 4 : 100);
      }, 50);
    } else if (scanResult) {
      setProgress(100);
    }
    return () => clearInterval(interval);
  }, [isScanning, scanResult]);

  return (
    <AnimatePresence>
      {showOptimizationResults && (
        <motion.div
           className="fixed z-[100] right-[2%] top-1/2 -translate-y-1/2 w-[380px] select-none pointer-events-auto max-h-[95vh] flex flex-col"
           initial={{ x: 100, opacity: 0, scale: 0.95 }}
           animate={{ x: 0, opacity: 1, scale: 1 }}
           exit={{ x: 100, opacity: 0, scale: 0.95 }}
           transition={{ type: 'spring', damping: 28, stiffness: 200 }}
        >
          {/* Main Container with Scroll */}
          <div className="flex flex-col h-full bg-[#020c18]/70 backdrop-blur-3xl border border-white/10 rounded-2xl shadow-[0_80px_200px_rgba(0,0,0,1)] overflow-hidden">
            
            {/* Glossy Header Bar */}
            <div className="p-7 pb-5 flex justify-between items-center bg-gradient-to-b from-white/[0.08] to-transparent border-b border-white/10 sticky top-0 z-20 backdrop-blur-3xl">
               <div className="flex flex-col gap-2">
                  <div className="flex items-center gap-3">
                     <div className="w-3 h-3 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_15px_#00f5ff]" />
                     <div className="font-orbitron text-[13px] font-black text-white tracking-[7px] uppercase">MISSION_INTEL_SYSTEM</div>
                  </div>
                  <div className="font-mono-tech text-[9px] text-cyan-400 font-medium uppercase tracking-[4px]">SECTOR: {selectedCountry?.name || 'GLOBAL'} // LAT: {selectedCountry?.lat.toFixed(2)} // LNG: {selectedCountry?.lng.toFixed(2)}</div>
               </div>
               <button 
                  onClick={() => setShowOptimizationResults(false)}
                  className="w-12 h-12 flex items-center justify-center rounded-full border border-white/10 hover:border-cyan-400/50 hover:bg-cyan-400/20 text-white/50 hover:text-cyan-400 transition-all group shadow-inner"
               >
                  <span className="text-2xl font-light transform group-hover:rotate-90 transition-transform">✕</span>
               </button>
            </div>

            {/* Scrollable Content */}
            <div className="p-7 overflow-y-auto no-scrollbar max-h-[calc(95vh-120px)]">
               
               {/* High Impact Progress Section */}
               <div className="mb-8 p-7 bg-cyan-400/[0.05] border border-cyan-400/20 rounded-2xl relative overflow-hidden group shadow-2xl">
                  <div className="absolute top-0 right-0 p-5">
                     <div className="flex items-center gap-3 font-mono-tech text-[10px] text-cyan-400 font-bold tracking-[3px]">
                        <motion.div animate={{ opacity: [1, 0.5, 1] }} transition={{ repeat: Infinity, duration: 1.5 }}>LINK_STABLE</motion.div>
                        <div className="w-1.5 h-4 bg-cyan-400/30" />
                        <span>TX: OK</span>
                     </div>
                  </div>
                  
                  <div className="flex items-baseline gap-2 mb-6">
                     <motion.div className="text-8xl font-black text-white tabular-nums tracking-tighter drop-shadow-[0_0_40px_#00f5ff70]">
                        {Math.floor(progress)}
                     </motion.div>
                     <div className="text-3xl font-orbitron text-cyan-400 font-bold opacity-60">%</div>
                  </div>

                  <div className="relative h-2.5 w-full bg-black/60 rounded-full overflow-hidden border border-white/10 shadow-inner">
                     <motion.div 
                        className="h-full bg-gradient-to-r from-cyan-600 via-cyan-400 to-white shadow-[0_0_30px_#00f5ff]" 
                        initial={{ width: 0 }} 
                        animate={{ width: `${progress}%` }} 
                        transition={{ duration: 0.5 }}
                     />
                     {/* Segment markers */}
                     <div className="absolute inset-0 flex justify-between px-2 pointer-events-none">
                        {[...Array(15)].map((_, i) => <div key={i} className="w-px h-full bg-black/40" />)}
                     </div>
                  </div>
                  
                  <div className="mt-5 flex justify-between font-mono-tech text-[9px] text-cyan-400 font-bold tracking-[5px] uppercase opacity-40">
                     <span>PARALLEL_CALC_ACTIVE</span>
                     <span>λ_LATENCY: 0.14MS</span>
                  </div>
               </div>

               {/* Mission Profile */}
               <TacticalBox title="DEPLOYMENT_SUMMARY">
                  <DataRow label="MISSION_MODE" value={missionMode} color="#00f5ff" />
                  <DataRow label="ANALYSIS_TYPE" value={scanResult?.mission?.type || "ORBITAL_ASSESSMENT"} />
                  <DataRow label="CONFIDENCE_LVL" value="ULTIMATUM" color="#00ffcc" />
                  <DataRow label="HORIZON_SCOPE" value={`${scanResult?.mission?.analysis_horizon_hours || 24} HOURS`} />
               </TacticalBox>

               {/* Performance Data */}
               <AnimatePresence>
                  {(scanResult || progress > 30) && (
                     <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
                        <TacticalBox title="REALTIME_METRICS">
                           <DataRow label="KAPSAMA_ORANI" value={`${((scanResult?.performance?.point_coverage_pct || 0.9998) * 100).toFixed(3)}%`} color="#00ffcc" />
                           <DataRow label="TEMSIL_SURESI" value={`${scanResult?.performance?.avg_revisit_time_s || '88.4'} SEC`} />
                           <DataRow label="MAX_GECIKME" value={`${scanResult?.performance?.max_gap_duration_s || '132.1'} SEC`} />
                           <DataRow label="SYSTEM_LIMIT" value={`${scanResult?.performance?.worst_case_gap_s || '194.5'} SEC`} />
                        </TacticalBox>
                     </motion.div>
                  )}
               </AnimatePresence>

               {/* Hardware / Constellation info */}
               <AnimatePresence>
                  {(scanResult || progress > 60) && (
                     <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
                        <TacticalBox title="CONSTELLATION_PARAMS">
                           <DataRow label="AKTIF_UYDU_SAYISI" value={scanResult?.satellites?.length || '48'} color="#00f5ff" />
                           <DataRow label="YORUNGE_DUZLEMI" value={scanResult?.parameters?.planes || '6'} />
                           <DataRow label="DUZLEM_ICI_UYDU" value={scanResult?.parameters?.satellites_per_plane || '8'} />
                           <DataRow label="IRT_MESAFESI" value={`${(scanResult?.parameters?.altitude_km || 550).toFixed(0)} KM`} />
                           <DataRow label="YORUNGE_EGIMI" value={`${(scanResult?.parameters?.inclination_deg || 53.0).toFixed(1)}°`} />
                        </TacticalBox>
                     </motion.div>
                  )}
               </AnimatePresence>

               {/* Optimization Logic */}
               {scanResult && (
                  <TacticalBox title="SOLVER_OVERVIEW">
                     <DataRow label="OPTIMIZATION_GOAL" value={scanResult?.optimization?.primary_goal || "MINIMIZE_GAP"} color="#00ffcc" />
                     <DataRow label="ALGORITHMIC_MODEL" value="ASYNC_HEURISTIC_V2" />
                  </TacticalBox>
               )}

               {/* Footer */}
               <div className="mt-10 text-center border-t border-white/10 pt-10 pb-6">
                  <div className="font-orbitron font-black text-[14px] tracking-[12px] text-cyan-400 mb-3 ml-[12px]">PRISM</div>
                  <div className="font-mono-tech text-[8px] tracking-[5px] uppercase text-white/40">GENESIS_OPTIMIZATION_UPLINK</div>
               </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
