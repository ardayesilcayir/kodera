'use client';

import { motion } from 'framer-motion';
import { usePrismStore } from '@/lib/store';
import { useRouter } from 'next/navigation';

const MODES = ['BALANCED', 'EMERGENCY_COMMS', 'EARTH_OBSERVATION', 'BROADCAST'] as const;

export default function Header() {
  const { missionMode, setMissionMode } = usePrismStore();
  const router = useRouter();

  const handleModeClick = () => {
    const currentIndex = MODES.indexOf(missionMode);
    const nextIndex = (currentIndex + 1) % MODES.length;
    setMissionMode(MODES[nextIndex]);
  };
  return (
    <motion.div
      className="absolute top-0 left-1/2 flex flex-col items-center pt-8 z-20 select-none w-[90vw] max-w-[1200px]"
      style={{ pointerEvents: 'none', transform: 'translateX(-50%)' }}
      initial={{ y: -40, x: '-50%', opacity: 0 }}
      animate={{ y: 0, x: '-50%', opacity: 1 }}
      transition={{ duration: 1, delay: 0.3, ease: 'easeOut' }}
    >
      {/* Decorative top line */}
      <motion.div
        className="mb-4 flex items-center gap-3"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 1.5, delay: 0.5 }}
      >
        <div className="h-px w-24" style={{ background: 'linear-gradient(90deg, transparent, rgba(0,245,255,0.6))' }} />
        <motion.div
          className="w-1.5 h-1.5 rounded-full"
          style={{ background: '#00f5ff' }}
          animate={{ opacity: [1, 0.2, 1], scale: [1, 1.5, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
        <div className="h-px w-24" style={{ background: 'linear-gradient(90deg, rgba(0,245,255,0.6), transparent)' }} />
      </motion.div>

      {/* Title */}
      <motion.h1
        className="font-orbitron gradient-text"
        style={{
          fontSize: 'clamp(20px, 3vw, 36px)',
          fontWeight: 800,
          letterSpacing: '6px',
          textAlign: 'center',
          lineHeight: 1.1,
          marginBottom: '6px',
          filter: 'drop-shadow(0 0 20px rgba(0,245,255,0.5))',
        }}
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.4 }}
      >
        PRISM ORBIT COMMAND
      </motion.h1>

      {/* Subtitle */}
      <motion.div
        className="flex items-center gap-2"
        style={{ pointerEvents: 'auto' }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        <span
          className="font-mono-tech"
          style={{ fontSize: '12px', color: 'rgba(0,245,255,0.5)', letterSpacing: '2px' }}
        >
          Mission Control Interface •
        </span>
        <span
          className="font-mono-tech"
          style={{ fontSize: '12px', color: 'rgba(0,245,255,0.4)', letterSpacing: '2px' }}
        >
          System Status:
        </span>
        <motion.span
          className="font-orbitron"
          style={{ fontSize: '11px', color: '#00ffcc', letterSpacing: '2px', fontWeight: 600, cursor: 'pointer' }}
          animate={{ opacity: [1, 0.5, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
          onClick={handleModeClick}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {missionMode}
        </motion.span>
      </motion.div>

      {/* Bottom decorative + Logout */}
      <motion.div
        className="mt-3 flex items-center gap-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        <div className="flex items-center gap-2">
          {[...Array(3)].map((_, i) => (
            <motion.div
              key={i}
              className="rounded-full"
              style={{
                width: i === 1 ? '12px' : '4px',
                height: '2px',
                background: '#00f5ff',
              }}
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, delay: i * 0.2, repeat: Infinity }}
            />
          ))}
        </div>

        <button 
          onClick={() => router.push('/login')}
          style={{ 
            pointerEvents: 'auto',
            background: 'none', 
            border: 'none', 
            color: 'rgba(255, 20, 147, 0.6)', 
            fontFamily: 'Share Tech Mono', 
            fontSize: '9px', 
            letterSpacing: '3px',
            cursor: 'pointer',
            padding: '4px 8px',
            borderBottom: '1px solid transparent',
            transition: 'all 0.3s'
          }}
          className="hover:text-pink-400 hover:border-pink-500 hover:drop-shadow-[0_0_8px_rgba(255,20,147,0.5)]"
        >
          DISCONNECT_UPLINK
        </button>

        <div className="flex items-center gap-2">
          {[...Array(3)].map((_, i) => (
            <motion.div
              key={i}
              className="rounded-full"
              style={{
                width: i === 1 ? '12px' : '4px',
                height: '2px',
                background: '#00f5ff',
              }}
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, delay: i * 0.2, repeat: Infinity }}
            />
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}
