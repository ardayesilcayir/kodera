'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePrismStore, CountryData } from '@/lib/store';

interface CountryPanelProps {
  country: CountryData | null;
  onClose: () => void;
}

export default function CountryInfoPanel({ country, onClose }: CountryPanelProps) {
  const surfaceTarget = usePrismStore((s) => s.surfaceTarget);
  const isScanning = usePrismStore((s) => s.isScanning);
  const scanResult = usePrismStore((s) => s.scanResult);
  const scanError = usePrismStore((s) => s.scanError);
  const [progress, setProgress] = useState(0);

  const latStr = surfaceTarget?.lat.toFixed(5) ?? country?.lat.toFixed(5) ?? '—';
  const lngStr = surfaceTarget?.lng.toFixed(5) ?? country?.lng.toFixed(5) ?? '—';

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isScanning) {
      setProgress(0);
      interval = setInterval(() => {
        setProgress(p => {
          if (p < 50) return p + Math.random() * 2 + 0.5;
          if (p < 78) return p + Math.random() * 0.5 + 0.1;
          if (p < 90) return p + Math.random() * 0.12;
          return p;
        });
      }, 120);
    } else if (scanResult) {
      setProgress(100);
    } else {
      setProgress(0);
    }
    return () => clearInterval(interval);
  }, [isScanning, scanResult]);

  const handleCalculate = async () => {
    const { runScan, setShowOptimizationResults, setCameraZoomed } = usePrismStore.getState();
    setShowOptimizationResults(true);
    setCameraZoomed(true);
    await runScan();
  };

  return (
    <AnimatePresence>
      {country && (
        <motion.div
          className="fixed z-50 select-none pointer-events-auto"
          style={{ bottom: '110px', left: '50%', x: '-50%' }}
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 20, opacity: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          <motion.div
            className="glass-panel scanlines relative overflow-hidden"
            style={{ width: '280px', padding: '32px 24px' }}
            whileHover={isScanning ? {} : { borderColor: 'rgba(0,245,255,0.6)' }}
          >
            {/* HUD corners */}
            <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-cyan-400 opacity-70" />
            <div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-cyan-400 opacity-70" />
            <div className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-cyan-400 opacity-70" />
            <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-cyan-400 opacity-70" />

            {/* Close */}
            <button
              type="button"
              onClick={onClose}
              disabled={isScanning}
              className="absolute top-2.5 right-2.5 w-7 h-7 flex items-center justify-center rounded border transition-all z-20 disabled:opacity-20 disabled:pointer-events-none group/close"
              style={{
                borderColor: 'rgba(0,245,255,0.25)',
                background: 'rgba(0,10,20,0.6)',
              }}
            >
              <svg width="10" height="10" viewBox="0 0 10 10" className="text-[rgba(0,245,255,0.5)] group-hover/close:text-[#00f5ff] transition-colors">
                <line x1="1" y1="1" x2="9" y2="9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                <line x1="9" y1="1" x2="1" y2="9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </button>

            {/* Title */}
            <div className="text-center mb-3 relative z-10">
              <span className="font-orbitron text-xs font-bold tracking-widest text-neon" style={{ fontSize: '11px', letterSpacing: '3px' }}>
                {country.name}
              </span>
            </div>

            {/* Divider */}
            <div className="w-full h-px mb-4 relative z-10" style={{ background: 'linear-gradient(90deg, transparent, rgba(0,245,255,0.4), transparent)' }} />

            {/* Info rows */}
            <div className="space-y-3 mb-5 relative z-10">
              <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
                <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">REGION</span>
                <span className="font-mono-tech text-[10px] text-[#00f5ff]">{country.region}</span>
              </div>
              <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
                <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">LAT</span>
                <span className="font-mono-tech text-[10px] text-[#00f5ff] tabular-nums">{latStr}°</span>
              </div>
              <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
                <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">LNG</span>
                <span className="font-mono-tech text-[10px] text-[#00f5ff] tabular-nums">{lngStr}°</span>
              </div>
              <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
                <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">STATUS</span>
                <span className="font-mono-tech text-[10px] flex items-center gap-1.5" style={{ color: isScanning ? '#f59e0b' : scanResult ? '#00ffcc' : scanError ? '#f87171' : '#00f5ff' }}>
                  <div className={`w-1.5 h-1.5 rounded-full ${isScanning ? 'animate-pulse' : ''}`} style={{ background: isScanning ? '#f59e0b' : scanResult ? '#00ffcc' : scanError ? '#f87171' : '#00f5ff' }} />
                  {isScanning ? 'SCANNING' : scanResult ? 'LOCKED' : scanError ? 'ERROR' : 'READY'}
                </span>
              </div>
            </div>

            {/* Progress bar — visible when scanning or complete */}
            {(isScanning || scanResult) && (
              <div className="mb-4 relative z-10">
                <div className="flex justify-between items-center mb-1.5">
                  <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.5)] tracking-[2px] uppercase">
                    {isScanning ? 'CALCULATING' : 'COMPLETE'}
                  </span>
                  <span className="font-orbitron text-[10px] font-bold" style={{ color: scanResult ? '#00ffcc' : '#00f5ff' }}>
                    {Math.floor(progress)}%
                  </span>
                </div>
                <div className="h-1.5 w-full rounded-full overflow-hidden bg-[rgba(0,10,20,0.6)] border border-[rgba(0,245,255,0.15)]">
                  <motion.div
                    className="h-full rounded-full"
                    style={{
                      background: scanResult
                        ? 'linear-gradient(90deg, #059669, #00ffcc)'
                        : 'linear-gradient(90deg, #0891b2, #00f5ff)',
                      boxShadow: scanResult ? '0 0 10px #00ffcc' : '0 0 10px #00f5ff',
                    }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.3, ease: 'easeOut' }}
                  />
                </div>
              </div>
            )}

            {/* Error */}
            {scanError && (
              <div className="mb-4 p-2 rounded bg-[rgba(248,113,113,0.08)] border border-[rgba(248,113,113,0.15)] relative z-10">
                <span className="font-mono-tech text-[8px] text-red-400/80 break-words">{scanError}</span>
              </div>
            )}

            {/* Action Button */}
            <motion.button
              className="btn-neon w-full font-orbitron relative z-10 disabled:opacity-40 disabled:cursor-wait disabled:pointer-events-none"
              style={{ background: scanResult ? 'rgba(0,255,204,0.08)' : 'rgba(0,245,255,0.1)' }}
              whileHover={isScanning ? {} : { scale: 1.04 }}
              whileTap={isScanning ? {} : { scale: 0.96 }}
              onClick={handleCalculate}
              disabled={isScanning}
            >
              {isScanning ? 'CALCULATING...' : scanResult ? 'RE-CALCULATE' : 'GENERATE ORBIT'}
            </motion.button>

            {/* Animated accent line */}
            <motion.div
              className="absolute bottom-0 left-0 h-0.5"
              style={{ background: 'linear-gradient(90deg, transparent, #00f5ff, transparent)' }}
              animate={{ width: ['0%', '100%', '0%'] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
            />
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
