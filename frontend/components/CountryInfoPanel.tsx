'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { usePrismStore, CountryData } from '@/lib/store';

interface CountryPanelProps {
  country: CountryData | null;
  onClose: () => void;
}

export default function CountryInfoPanel({ country, onClose }: CountryPanelProps) {
  return (
    <AnimatePresence>
      {country && (
        <motion.div
           className="country-panel fixed z-[150] select-none pointer-events-auto overflow-hidden shadow-[0_40px_100px_rgba(0,0,0,0.8)]"
           style={{
             bottom: '120px',
             left: '50%',
             width: '380px',
             background: 'rgba(5, 12, 24, 0.75)',
             backdropFilter: 'blur(35px)',
             WebkitBackdropFilter: 'blur(35px)',
             border: '1px solid rgba(0, 245, 255, 0.15)',
             padding: '28px 32px',
             transformOrigin: 'bottom center',
           }}
           initial={{ x: '-50%', y: 40, opacity: 0, scale: 0.95 }}
           animate={{ x: '-50%', y: 0, opacity: 1, scale: 1 }}
           exit={{ x: '-50%', y: 40, opacity: 0, scale: 0.95 }}
           transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        >
          {/* Minimalist Close X (Top Left) */}
          <button
            onClick={onClose}
            className="absolute top-6 left-8 w-8 h-8 flex items-center justify-center text-[#00f5ff] opacity-30 hover:opacity-100 transition-all z-20 group"
          >
             <span className="text-xl drop-shadow-[0_0_8px_#00f5ff] font-light">✕</span>
             <motion.div 
                className="absolute inset-0 border border-[#00f5ff]/20 rounded-full"
                whileHover={{ scale: 1.1, borderColor: 'rgba(0, 245, 255, 0.6)' }}
             />
          </button>

          {/* Target Header */}
          <div className="text-center mb-8 relative z-10">
            <div className="font-orbitron text-[8px] text-[#00f5ff] tracking-[10px] opacity-40 mb-2 uppercase flex items-center justify-center gap-3">
               <div className="w-1 h-1 bg-[#00f5ff]" /> SURFACE_LOCK <div className="w-1 h-1 bg-[#00f5ff]" />
            </div>
            <h2 className="font-orbitron text-3xl font-black text-white tracking-widest uppercase drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]">
               {country.name}
            </h2>
            <div className="font-mono-tech text-[10px] text-[#00ffcc] mt-1 tracking-[4px] opacity-40 uppercase">{country.region}</div>
          </div>

          {/* Tactical Metrics Grid (Sleek Mode) */}
          <div className="grid grid-cols-2 gap-px bg-[#00f5ff]/10 rounded-sm overflow-hidden mb-8 border border-[#00f5ff]/10">
             <div className="bg-[#050c18]/80 p-4 group">
                <div className="font-mono-tech text-[7px] text-white/20 tracking-[2px] uppercase mb-1">Latitude</div>
                <div className="font-orbitron text-xl font-bold text-white tracking-tighter">
                   {country.lat > 0 ? '+' : ''}{country.lat.toFixed(2)}°
                </div>
             </div>
             
             <div className="bg-[#050c18]/80 p-4 group">
                <div className="font-mono-tech text-[7px] text-white/20 tracking-[2px] uppercase mb-1">Longitude</div>
                <div className="font-orbitron text-xl font-bold text-white tracking-tighter">{country.lng > 0 ? '+' : ''}{country.lng.toFixed(2)}°</div>
             </div>

             <div className="bg-[#050c18]/80 p-5 col-span-2 group">
                <div className="flex justify-between items-center mb-1">
                   <div className="font-mono-tech text-[8px] text-white/20 uppercase tracking-[3px]">Uplink_Signal</div>
                   <div className="flex gap-1 h-2">
                       {[...Array(5)].map((_, i) => (
                           <motion.div 
                              key={i} 
                              className="w-1 rounded-full" 
                              style={{ background: country.signalStrength > (i * 20) ? '#00ffcc' : 'rgba(255,255,255,0.05)' }} 
                           />
                       ))}
                   </div>
                </div>
                <div className="font-orbitron text-2xl font-bold text-[#00ffcc] tracking-tighter">{country.signalStrength}%</div>
             </div>
          </div>

          {/* Tactical Metadata */}
          <div className="flex justify-between items-center px-2 opacity-30 mt-2">
             <div className="font-mono-tech text-[6px] text-white/60 tracking-[4px] uppercase">Auth: PSM_A1_LOCK</div>
             <div className="font-mono-tech text-[6px] text-white/60 tracking-[4px] uppercase text-right">STAT: SECURE</div>
          </div>
          
          {/* Corner Decors */}
          <div className="absolute top-0 right-0 w-8 h-8 border-t border-r border-[#00f5ff]/20" />
          <div className="absolute bottom-0 left-0 w-8 h-8 border-b border-l border-[#00f5ff]/20" />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
