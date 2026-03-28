'use client';

import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { usePrismStore } from '@/lib/store';

export default function ProfilePanel() {
  const router = useRouter();

  return (
    <motion.div
      className="glass-panel scanlines relative overflow-hidden select-none cursor-pointer group"
      style={{
        width: '280px',
        padding: '32px 24px',
      }}
      initial={{ x: -60, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 1, delay: 0.5, ease: 'easeOut' }}
      whileHover={{ scale: 1.03, borderColor: 'rgba(0,245,255,0.6)' }}
      onClick={() => router.push('/profile')}
    >
      {/* HUD corners */}
      <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-cyan-400 opacity-70" />
      <div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-cyan-400 opacity-70" />
      <div className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-cyan-400 opacity-70" />
      <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-cyan-400 opacity-70" />

      {/* User Icon */}
      <div className="flex justify-center mb-4 relative z-10">
        <motion.div
          className="w-12 h-12 rounded-full flex items-center justify-center transition-shadow group-hover:shadow-[0_0_30px_rgba(0,245,255,0.6)]"
          style={{
            border: '1px solid rgba(0,245,255,0.4)',
            background: 'rgba(0,245,255,0.05)',
            boxShadow: '0 0 20px rgba(0,245,255,0.2)',
          }}
          animate={{ boxShadow: ['0 0 10px rgba(0,245,255,0.2)', '0 0 25px rgba(0,245,255,0.5)', '0 0 10px rgba(0,245,255,0.2)'] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00f5ff" strokeWidth="1.5">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
        </motion.div>
      </div>

      {/* Label */}
      <div className="text-center mb-3 relative z-10">
        <span
          className="font-orbitron text-xs font-bold tracking-widest text-neon"
          style={{ fontSize: '11px', letterSpacing: '3px' }}
        >
          'OPERATOR PROFILE'
        </span>
      </div>

      {/* Divider */}
      <div
        className="w-full h-px mb-4 relative z-10"
        style={{ background: 'linear-gradient(90deg, transparent, rgba(0,245,255,0.4), transparent)' }}
      />

      {/* Content */}
      <div className="space-y-3 mb-6 relative z-10">
        <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
          <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">ID</span>
          <span className="font-mono-tech text-[10px] text-[#00f5ff]">GHOST-01</span>
        </div>
        <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
          <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">CLEARANCE</span>
          <span className="font-mono-tech text-[10px] text-[#00ffcc]">LEVEL 5</span>
        </div>
        <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
          <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">STATUS</span>
          <span className="font-mono-tech text-[10px] text-[#00f5ff] flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 bg-[#00ffcc] rounded-full animate-pulse" /> ACTIVE
          </span>
        </div>
      </div>

      {/* Button */}
      <motion.button
        className="btn-neon w-full font-orbitron relative z-10 bg-[rgba(0,245,255,0.1)]"
        whileHover={{ scale: 1.04 }}
        whileTap={{ scale: 0.96 }}
      >
        ACCESS DOSSIER
      </motion.button>

      {/* Animated accent line */}
      <motion.div
        className="absolute bottom-0 left-0 h-0.5"
        style={{ background: 'linear-gradient(90deg, transparent, #00f5ff, transparent)' }}
        animate={{ width: ['0%', '100%', '0%'] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      />
    </motion.div>
  );
}
