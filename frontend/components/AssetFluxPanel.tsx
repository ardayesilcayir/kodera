'use client';

import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { usePrismStore } from '@/lib/store';

export default function AssetFluxPanel() {
  const router = useRouter();
  const { selectedCountry } = usePrismStore();

  return (
    <div
      className="glass-panel scanlines fixed z-[100] select-none pointer-events-auto"
      style={{
        width: '280px',
        padding: '32px 24px',
        right: 'link' in { link: '4%' } ? '4%' : '4%', // Ensuring absolute positioning
        top: '50%',
        transform: 'translateY(-50%)',
        opacity: 1, // Fixed visibility
        pointerEvents: 'auto'
      }}
    >
      {/* HUD corners */}
      <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-cyan-400 opacity-70" />
      <div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-cyan-400 opacity-70" />
      <div className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-cyan-400 opacity-70" />
      <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-cyan-400 opacity-70" />

      {/* Mission Icon (Persistent Heartbeat) */}
      <div className="flex justify-center mb-4 relative z-10">
        <motion.div
          className="w-12 h-12 rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(0,245,255,0.2)]"
          style={{
            border: '1px solid rgba(0,245,255,0.4)',
            background: 'rgba(0,10,20,0.4)',
          }}
          animate={{ boxShadow: ['0 0 10px rgba(0,245,255,0.2)', '0 0 25px rgba(0,245,255,0.5)', '0 0 10px rgba(0,245,255,0.2)'] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00f5ff" strokeWidth="1.5">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
          </svg>
        </motion.div>
      </div>

      {/* Label */}
      <div className="text-center mb-3 relative z-10">
        <span
          className="font-orbitron font-bold tracking-[4px] text-[#00f5ff]"
          style={{ fontSize: '11px' }}
        >
          MISSION_PROTOCOL
        </span>
      </div>

      {/* Divider */}
      <div
        className="w-full h-px mb-4 relative z-10"
        style={{ background: 'linear-gradient(90deg, transparent, rgba(0,245,255,0.4), transparent)' }}
      />

      {/* Static Sector Display */}
      <div className="space-y-3 mb-6 relative z-10 text-center">
        <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2.5 rounded">
          <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.6)] uppercase">TGT_SECTOR</span>
          <span className="font-mono-tech text-[10px] text-[#00f5ff] uppercase truncate max-w-[120px]">
             {selectedCountry ? selectedCountry.name : 'ALL_GLOBAL'}
          </span>
        </div>
        <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2.5 rounded">
          <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.6)] uppercase">STAT_LINK</span>
          <span className="font-mono-tech text-[10px] text-[#00ffcc] flex items-center gap-1.5 uppercase">
            <div className={`w-1.5 h-1.5 rounded-full ${selectedCountry ? 'bg-[#ffcc00]' : 'bg-[#00ffcc] shadow-[0_0_8px_#00ffcc]'}`} /> 
            {selectedCountry ? 'READY' : 'STANDBY'}
          </span>
        </div>
      </div>

      {/* Persistent Initializer Button */}
      <motion.button
        className="w-full font-orbitron py-3.5 text-[10px] tracking-[4px] font-black relative z-10 bg-[rgba(0,245,255,0.05)] border border-[#00f5ff]/30 text-[#00f5ff] hover:bg-[#00f5ff] hover:text-black transition-all"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => router.push('/scan')}
      >
        INITIALIZE SCAN
      </motion.button>

      {/* Footer Branding Line */}
      <div className="mt-4 text-center opacity-10">
         <div className="font-mono-tech text-[6px] tracking-[6px] uppercase">PRISM_MISSION_CONTROL</div>
      </div>

      {/* Animated accent line */}
      <motion.div
        className="absolute bottom-0 left-0 h-0.5"
        style={{ background: 'linear-gradient(90deg, transparent, #00f5ff, transparent)' }}
        animate={{ width: ['0%', '100%', '0%'] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      />
    </div>
  );
}
