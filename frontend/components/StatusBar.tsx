'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import { motion, animate } from 'framer-motion';
import { usePrismStore, SIM_SPEED_MIN, SIM_SPEED_MAX, SIM_SPEED_STEP } from '@/lib/store';

/** YouTube benzeri çift ok — yavaşlat / hızlandır */
function IconDoubleChevronLeft({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path
        d="M11 5l-7 7 7 7M18 5l-7 7 7 7"
        stroke="currentColor"
        strokeWidth="2.25"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconDoubleChevronRight({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path
        d="M13 5l7 7-7 7M6 5l7 7-7 7"
        stroke="currentColor"
        strokeWidth="2.25"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function SimSpeedBlock({
  simulationSpeedMultiplier,
  adjustSimulationSpeed,
  setSimulationSpeedMultiplier,
}: {
  simulationSpeedMultiplier: number;
  adjustSimulationSpeed: (direction: -1 | 1) => void;
  setSimulationSpeedMultiplier: (value: number) => void;
}) {
  const [draft, setDraft] = useState(() => simulationSpeedMultiplier.toFixed(2));
  const focusedRef = useRef(false);

  useEffect(() => {
    if (!focusedRef.current) {
      setDraft(simulationSpeedMultiplier.toFixed(2));
    }
  }, [simulationSpeedMultiplier]);

  const commitDraft = useCallback(() => {
    const normalized = draft.replace(',', '.').trim();
    const n = parseFloat(normalized);
    if (Number.isFinite(n)) {
      setSimulationSpeedMultiplier(n);
      setDraft(Math.min(SIM_SPEED_MAX, Math.max(SIM_SPEED_MIN, n)).toFixed(2));
    } else {
      setDraft(simulationSpeedMultiplier.toFixed(2));
    }
  }, [draft, setSimulationSpeedMultiplier, simulationSpeedMultiplier]);

  return (
    <motion.div
      className="px-3"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 2.2 }}
    >
      <div className="font-orbitron mb-1 text-[8px] uppercase tracking-[0.2em] text-[rgba(0,245,255,0.55)]">
        EARTH · SIM SPEED
      </div>
      <div className="sim-speed-panel">
        <button
          type="button"
          aria-label="Simülasyon hızını azalt"
          disabled={simulationSpeedMultiplier <= SIM_SPEED_MIN}
          onClick={() => adjustSimulationSpeed(-1)}
          className="sim-speed-btn"
        >
          <IconDoubleChevronLeft />
        </button>

        <div className="relative z-[1] flex items-center gap-0.5">
          <input
            type="text"
            inputMode="decimal"
            aria-label="Simülasyon hız çarpanı"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onFocus={() => {
              focusedRef.current = true;
            }}
            onBlur={() => {
              focusedRef.current = false;
              commitDraft();
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                (e.target as HTMLInputElement).blur();
              }
            }}
            className="sim-speed-input"
          />
          <span className="sim-speed-mult" aria-hidden>
            ×
          </span>
        </div>

        <button
          type="button"
          aria-label="Simülasyon hızını artır"
          disabled={simulationSpeedMultiplier >= SIM_SPEED_MAX}
          onClick={() => adjustSimulationSpeed(1)}
          className="sim-speed-btn"
        >
          <IconDoubleChevronRight />
        </button>
      </div>
      <div className="font-mono-tech mt-1.5 text-[6px] tracking-[0.15em] text-white/30">
        RANGE {SIM_SPEED_MIN.toFixed(2)}× — {SIM_SPEED_MAX.toFixed(0)}× · STEP {SIM_SPEED_STEP}
      </div>
    </motion.div>
  );
}

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
  const orbitalAssets = usePrismStore((s) => s.orbitalAssets);
  const signalStrength = usePrismStore((s) => s.signalStrength);
  const powerStatus = usePrismStore((s) => s.powerStatus);
  const simulationSpeedMultiplier = usePrismStore((s) => s.simulationSpeedMultiplier);
  const adjustSimulationSpeed = usePrismStore((s) => s.adjustSimulationSpeed);
  const setSimulationSpeedMultiplier = usePrismStore((s) => s.setSimulationSpeedMultiplier);
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
        flexWrap: 'wrap',
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

      <div
        className="h-8 w-px mx-1"
        style={{ background: 'linear-gradient(180deg, transparent, rgba(0,245,255,0.25), transparent)' }}
      />

      <SimSpeedBlock
        simulationSpeedMultiplier={simulationSpeedMultiplier}
        adjustSimulationSpeed={adjustSimulationSpeed}
        setSimulationSpeedMultiplier={setSimulationSpeedMultiplier}
      />

      {/* Inner glow gradient */}
      <div className="absolute inset-0 z-[-1] bg-gradient-to-r from-transparent via-[rgba(0,245,255,0.03)] to-transparent pointer-events-none" />
    </motion.div>
  );
}
