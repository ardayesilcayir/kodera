'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { usePrismStore, CountryData } from '@/lib/store';
import { useRouter } from 'next/navigation';

interface CountryPanelProps {
  country: CountryData | null;
  onClose: () => void;
}

export default function CountryInfoPanel({ country, onClose }: CountryPanelProps) {
  const router = useRouter();
  return (
    <AnimatePresence>
      {country && (
        <motion.div
           className="fixed z-50 select-none pointer-events-auto shadow-[0_40px_100px_rgba(0,0,0,0.8)]"
           style={{
             bottom: '110px',
             left: '50%',
             x: '-50%',
             width: '320px',
           }}
           initial={{ y: 20, opacity: 0, scale: 0.95 }}
           animate={{ y: 0, opacity: 1, scale: 1 }}
           exit={{ y: 20, opacity: 0, scale: 0.95 }}
           transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        >
          <div className="glass-panel scanlines p-6 border border-white/10 relative overflow-hidden bg-black/40 backdrop-blur-2xl rounded-2xl shadow-[0_25px_50px_-12px_rgba(0,0,0,0.5)]">
            
            {/* Elite Corner Accents */}
            <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-cyan-400/40" />
            <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-cyan-400/40" />
            <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-cyan-400/20" />
            <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-cyan-400/20" />

            <div className="absolute top-4 left-4">
               <button 
                onClick={onClose}
                className="w-8 h-8 flex items-center justify-center rounded-lg border border-white/5 hover:border-cyan-400/30 hover:bg-cyan-400/10 text-white/30 hover:text-cyan-400 transition-all"
               >
                 <span className="text-[10px]">✕</span>
               </button>
            </div>

            <div className="text-center mt-2">
               <div className="font-mono-tech text-[8px] text-cyan-400 tracking-[8px] uppercase opacity-40 mb-3 ml-[8px]">SURFACE_LOCK</div>
               <h2 className="text-2xl font-black text-white tracking-[6px] uppercase truncate px-2 leading-none mb-1">{country.name}</h2>
               <div className="font-mono-tech text-[9px] text-cyan-400/60 uppercase tracking-[4px] mb-8">{country.region}</div>
               
               <motion.button
                 className="w-full relative py-3 group overflow-hidden border border-white/10 rounded-lg bg-white/5 hover:bg-white/10 transition-all"
                 whileHover={{ scale: 1.02 }}
                 whileTap={{ scale: 0.98 }}
                 disabled={usePrismStore.getState().isScanning}
                 onClick={async () => {
                   const { runScan, setShowOptimizationResults, setCameraZoomed } = usePrismStore.getState();
                   setShowOptimizationResults(true);
                   setCameraZoomed(true);
                   await runScan();
                 }}
               >
                 <div className="relative z-10 font-orbitron text-[10px] font-black tracking-[4px] uppercase text-white/80 group-hover:text-white transition-colors">
                   {usePrismStore(s => s.isScanning) ? 'CALCULATING...' : 'INITIALIZE OPTIMIZATION'}
                 </div>
                 {/* Scanning pulse effect */}
                 <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/0 via-cyan-400/10 to-cyan-400/0 -translate-x-full group-hover:animate-shimmer" />
               </motion.button>

               <div className="mt-4 font-mono-tech text-[6px] text-white/20 tracking-[3px] uppercase">
                 PRISM_TARGETING_SERVICE v2.0
               </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
