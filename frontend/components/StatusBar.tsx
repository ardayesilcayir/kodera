'use client';

import { useEffect, useState } from 'react';
import { motion, animate } from 'framer-motion';
import { usePrismStore } from '@/lib/store';

function AnimatedNumber({ target }: { target: number }) {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const controls = animate(0, target, {
      duration: 1.5,
      ease: "easeOut",
      onUpdate(value) {
        setCurrent(Math.round(value));
      }
    });

    return () => {
      if (controls && typeof controls.stop === 'function') {
        controls.stop();
      }
    };
  }, [target]);

  return <span>{current}</span>;
}

export default function StatusBar() {
  const { orbitalAssets, signalStrength, powerStatus } = usePrismStore();
  const [utcTime, setUtcTime] = useState('');
  const [tick, setTick] = useState(false);
  const [liveAssets, setLiveAssets] = useState(orbitalAssets);
  const [liveSignal, setLiveSignal] = useState(signalStrength);

  useEffect(() => {
    const update = () => {
      const now = new Date();
      const h = now.getUTCHours().toString().padStart(2, '0');
      const m = now.getUTCMinutes().toString().padStart(2, '0');
      const s = now.getUTCSeconds().toString().padStart(2, '0');
      setUtcTime(`${h}:${m}:${s} UTC`);
      setTick(t => !t);
      
      // Real-time fluctuation simulations
      if (Math.random() > 0.6) {
        setLiveSignal(prev => Math.min(100, Math.max(82, prev + (Math.floor(Math.random() * 5) - 2))));
      }
      if (Math.random() > 0.8) {
        setLiveAssets(prev => Math.min(48, Math.max(42, prev + (Math.floor(Math.random() * 3) - 1))));
      }
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  const metrics = [
    {
      label: 'ORBITAL ASSETS',
      value: <><AnimatedNumber target={liveAssets} /> ACTIVE</>,
      icon: '◈',
      color: '#00f5ff',
    },
    {
      label: 'SIGNAL STRENGTH',
      value: <><AnimatedNumber target={liveSignal} />%</>,
      icon: '▲',
      color: '#00ffcc',
    },
    {
      label: 'LATENCY',
      value: <><AnimatedNumber target={14 + Math.floor(Math.random() * 3)} />ms</>,
      icon: '≋',
      color: '#00f5ff',
    },
    {
      label: 'ENCRYPTION',
      value: 'AES-512',
      icon: '❑',
      color: '#00ffcc',
    },
    {
      label: 'POWER SYSTEMS',
      value: <span style={{ color: '#00ffcc' }}>{powerStatus}</span>,
      icon: '⚡',
      color: '#00f5ff',
    },
    {
      label: 'LAST UPDATE',
      value: (
        <span className="font-mono-tech" style={{ fontSize: '13px' }}>
          <motion.span animate={{ opacity: tick ? 1 : 0.3 }} transition={{ duration: 0.1 }}>●</motion.span>
          {' '}{utcTime}
        </span>
      ),
      icon: '◷',
      color: '#00c8e0',
    },
  ];

  return (
    <motion.div
      className="glass-panel relative overflow-hidden select-none mx-auto"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        padding: '16px 24px',
        borderRadius: '16px',
        maxWidth: '1200px',
        background: 'rgba(0, 20, 40, 0.4)',
        border: '1px solid rgba(0, 245, 255, 0.2)',
        backdropFilter: 'blur(12px)',
        boxShadow: '0 8px 32px rgba(0,0,0,0.5), inset 0 0 20px rgba(0,245,255,0.05)',
      }}
      initial={{ y: 60, opacity: 0 }}
      animate={{ y: [0, -4, 0], opacity: 1 }}
      transition={{ 
        y: { duration: 5, repeat: Infinity, ease: 'easeInOut' },
        opacity: { duration: 1, delay: 0.8, ease: 'easeOut' }
      }}
    >


      {metrics.map((metric, i) => (
        <div key={metric.label} className="flex items-center">
          {/* Metric */}
          <motion.div
            className="flex items-center gap-3 px-6"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1 + i * 0.15 }}
          >
            <span style={{ color: metric.color, fontSize: '14px', opacity: 0.6 }}>{metric.icon}</span>
            <div>
              <div
                className="font-orbitron"
                style={{ fontSize: '8px', color: 'rgba(0,245,255,0.45)', letterSpacing: '2px', marginBottom: '2px' }}
              >
                {metric.label}
              </div>
              <div
                className="font-orbitron"
                style={{ fontSize: '13px', color: metric.color, fontWeight: 600, letterSpacing: '1px' }}
              >
                {metric.value}
              </div>
            </div>
          </motion.div>

          {/* Divider */}
          {i < metrics.length - 1 && (
            <div
              className="h-8 w-px"
              style={{ background: 'linear-gradient(180deg, transparent, rgba(0,245,255,0.25), transparent)' }}
            />
          )}
        </div>
      ))}

      {/* Inner glow gradient */}
      <div className="absolute inset-0 z-[-1] bg-gradient-to-r from-transparent via-[rgba(0,245,255,0.03)] to-transparent pointer-events-none" />
    </motion.div>
  );
}
