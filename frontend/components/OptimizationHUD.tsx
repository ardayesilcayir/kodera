'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { usePrismStore } from '@/lib/store';
import { useState, useEffect, useMemo } from 'react';

function InfoRow({ label, value, valueColor = '#00f5ff' }: { label: string; value: string; valueColor?: string }) {
  return (
    <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
      <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">{label}</span>
      <span className="font-mono-tech text-[10px]" style={{ color: valueColor }}>{value}</span>
    </div>
  );
}

export default function OptimizationHUD() {
  const { showOptimizationResults, selectedCountry, scanResult, isScanning, scanError, setShowOptimizationResults, missionMode } = usePrismStore();
  const [progress, setProgress] = useState(0);

  const rec = scanResult?.design.recommended;
  const metrics = rec?.metrics;
  const req = scanResult?.request;
  const ai = scanResult?.design.ai_engineering_summary;
  const explanations = scanResult?.design.explanations ?? [];

  const satsPerPlane = useMemo(() => {
    if (!rec?.total_satellites_T || !rec?.planes_P) return null;
    return Math.round(rec.total_satellites_T / rec.planes_P);
  }, [rec?.total_satellites_T, rec?.planes_P]);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isScanning) {
      setProgress(0);
      interval = setInterval(() => {
        setProgress(p => {
          if (p < 55) return p + Math.random() * 2.5 + 0.5;
          if (p < 80) return p + Math.random() * 0.6 + 0.1;
          if (p < 90) return p + Math.random() * 0.15;
          return p;
        });
      }, 120);
    } else if (scanResult) {
      setProgress(100);
    } else if (scanError) {
      setProgress(0);
    }
    return () => clearInterval(interval);
  }, [isScanning, scanResult, scanError]);

  return (
    <AnimatePresence>
      {showOptimizationResults && (
        <motion.div
          className="glass-panel scanlines relative overflow-hidden select-none"
          style={{ width: '280px', padding: '32px 24px', maxHeight: '70vh', display: 'flex', flexDirection: 'column' }}
          initial={{ x: 60, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 60, opacity: 0 }}
          transition={{ duration: 1, delay: 0.5, ease: 'easeOut' }}
          whileHover={{ borderColor: 'rgba(0,245,255,0.6)' }}
        >
          {/* HUD corners */}
          <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-cyan-400 opacity-70" />
          <div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-cyan-400 opacity-70" />
          <div className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-cyan-400 opacity-70" />
          <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-cyan-400 opacity-70" />

          {/* Icon */}
          <div className="flex justify-center mb-4 relative z-10">
            <motion.div
              className="w-12 h-12 rounded-full flex items-center justify-center transition-shadow"
              style={{
                border: '1px solid rgba(0,245,255,0.4)',
                background: 'rgba(0,245,255,0.05)',
                boxShadow: '0 0 20px rgba(0,245,255,0.2)',
              }}
              animate={{
                boxShadow: scanResult
                  ? ['0 0 10px rgba(0,255,204,0.2)', '0 0 25px rgba(0,255,204,0.5)', '0 0 10px rgba(0,255,204,0.2)']
                  : ['0 0 10px rgba(0,245,255,0.2)', '0 0 25px rgba(0,245,255,0.5)', '0 0 10px rgba(0,245,255,0.2)'],
              }}
              transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={scanResult ? '#00ffcc' : '#00f5ff'} strokeWidth="1.5">
                <circle cx="12" cy="12" r="10" />
                <ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)" />
                <ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(-60 12 12)" />
                <circle cx="12" cy="12" r="1.5" fill={scanResult ? '#00ffcc' : '#00f5ff'} />
              </svg>
            </motion.div>
          </div>

          {/* Label */}
          <div className="text-center mb-3 relative z-10">
            <span
              className="font-orbitron text-xs font-bold tracking-widest text-neon"
              style={{ fontSize: '11px', letterSpacing: '3px' }}
            >
              MISSION INTEL
            </span>
          </div>

          {/* Divider */}
          <div
            className="w-full h-px mb-4 relative z-10"
            style={{ background: 'linear-gradient(90deg, transparent, rgba(0,245,255,0.4), transparent)' }}
          />

          {/* Scrollable Content */}
          <div className="overflow-y-auto no-scrollbar flex-1 relative z-10">

            {/* Sector info */}
            <div className="space-y-3 mb-5">
              <InfoRow label="SECTOR" value={selectedCountry?.name || 'GLOBAL'} />
              <InfoRow label="MODE" value={missionMode} valueColor="#00ffcc" />
            </div>

            {/* Progress */}
            {(isScanning || scanResult || scanError) && (
              <div className="mb-5">
                <div className="flex justify-between items-center mb-1.5">
                  <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.5)] tracking-[2px] uppercase">PROGRESS</span>
                  <span className="font-orbitron text-[11px] font-bold" style={{ color: scanError ? '#f87171' : scanResult ? '#00ffcc' : '#00f5ff' }}>
                    {scanError ? 'ERROR' : `${Math.floor(progress)}%`}
                  </span>
                </div>
                <div className="h-1 w-full rounded-full overflow-hidden bg-[rgba(0,10,20,0.6)] border border-[rgba(0,245,255,0.1)]">
                  <motion.div
                    className="h-full rounded-full"
                    style={{
                      background: scanError ? '#f87171' : scanResult ? 'linear-gradient(90deg, #059669, #00ffcc)' : 'linear-gradient(90deg, #0891b2, #00f5ff)',
                      boxShadow: `0 0 8px ${scanError ? '#f87171' : scanResult ? '#00ffcc' : '#00f5ff'}`,
                    }}
                    animate={{ width: scanError ? '100%' : `${progress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
                <div className="font-mono-tech text-[7px] text-[rgba(0,245,255,0.3)] mt-1.5 tracking-wider">
                  {isScanning ? 'WALKER_ENUM + COVERAGE_SIM...' : scanResult ? 'OPTIMIZATION_COMPLETE' : scanError ? scanError : 'STANDBY'}
                </div>
              </div>
            )}

            {/* Error */}
            {scanError && (
              <div className="mb-5 p-2 rounded bg-[rgba(248,113,113,0.08)] border border-[rgba(248,113,113,0.2)]">
                <span className="font-mono-tech text-[8px] text-red-400/80 break-words">{scanError}</span>
              </div>
            )}

            {/* Loading skeleton */}
            {isScanning && !scanResult && (
              <motion.div className="space-y-3 mb-5" initial={{ opacity: 0 }} animate={{ opacity: 0.5 }}>
                {['SATELLITES', 'ALTITUDE', 'PLANES', 'COVERAGE'].map(k => (
                  <div key={k} className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.06)] p-2 rounded">
                    <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.3)]">{k}</span>
                    <motion.span
                      className="font-mono-tech text-[10px] text-[rgba(0,245,255,0.2)]"
                      animate={{ opacity: [0.2, 0.5, 0.2] }}
                      transition={{ repeat: Infinity, duration: 1.5 }}
                    >
                      ···
                    </motion.span>
                  </div>
                ))}
              </motion.div>
            )}

            {/* Results */}
            {scanResult && (
              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
                {rec ? (
                  <>
                    <div className="mb-1">
                      <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] tracking-[3px] uppercase">CONSTELLATION</span>
                    </div>
                    <div className="space-y-3 mb-5">
                      <InfoRow label="SATELLITES" value={String(rec.total_satellites_T)} />
                      <InfoRow label="PLANES" value={String(rec.planes_P)} />
                      <InfoRow label="SATS/PLANE" value={satsPerPlane != null ? String(satsPerPlane) : '—'} />
                      <InfoRow label="ALTITUDE" value={`${rec.altitude_km.toFixed(0)} KM`} valueColor="#00ffcc" />
                      <InfoRow label="INCLINATION" value={`${rec.inclination_deg.toFixed(1)}°`} />
                      <InfoRow label="FAMILY" value={String(rec.orbit_family ?? 'LEO')} valueColor="#00ffcc" />
                      <InfoRow label="WALKER T/P/F" value={`${rec.total_satellites_T}/${rec.planes_P}/${rec.phase_F}`} />
                    </div>

                    {metrics && (
                      <>
                        <div className="mb-1">
                          <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] tracking-[3px] uppercase">COVERAGE</span>
                        </div>
                        <div className="space-y-3 mb-5">
                          <InfoRow label="MIN_POINT" value={`${(metrics.min_point_coverage * 100).toFixed(2)}%`} valueColor="#00ffcc" />
                          <InfoRow label="MEAN" value={`${(metrics.mean_point_coverage * 100).toFixed(2)}%`} />
                          <InfoRow label="MAX_GAP" value={`${metrics.max_gap_seconds.toFixed(0)}s`} />
                          <InfoRow label="REVISIT_MED" value={`${metrics.revisit_median_seconds.toFixed(0)}s`} />
                          <InfoRow label="24/7" value={metrics.continuous_24_7_feasible ? 'FEASIBLE' : 'NOT_FEASIBLE'} valueColor={metrics.continuous_24_7_feasible ? '#00ffcc' : '#f87171'} />
                        </div>
                      </>
                    )}

                    <div className="mb-1">
                      <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] tracking-[3px] uppercase">SOLVER</span>
                    </div>
                    <div className="space-y-3 mb-5">
                      <InfoRow label="GOAL" value={req?.optimization?.primary_goal?.replace(/_/g, ' ') || '—'} />
                      <InfoRow label="COST" value={rec.cost_score.toFixed(4)} />
                      <InfoRow label="COMPLEXITY" value={rec.complexity_score.toFixed(4)} />
                    </div>
                  </>
                ) : (
                  <div className="p-2 rounded bg-[rgba(245,158,11,0.08)] border border-[rgba(245,158,11,0.2)] mb-5">
                    <span className="font-mono-tech text-[8px] text-amber-400/80">NO FEASIBLE SOLUTION</span>
                  </div>
                )}

                {ai && (
                  <div className="mb-5">
                    <div className="mb-1">
                      <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] tracking-[3px] uppercase">AI SUMMARY</span>
                    </div>
                    <div className="bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-3 rounded">
                      <p className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.6)] leading-relaxed whitespace-pre-line">{ai}</p>
                    </div>
                  </div>
                )}

                {explanations.length > 0 && (
                  <div className="mb-3">
                    <div className="mb-1">
                      <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] tracking-[3px] uppercase">ENGINE LOG</span>
                    </div>
                    <div className="bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-3 rounded space-y-1">
                      {explanations.slice(0, 5).map((line, i) => (
                        <div key={i} className="font-mono-tech text-[7px] text-[rgba(0,245,255,0.4)] leading-relaxed">
                          <span className="text-[rgba(0,245,255,0.25)] mr-1">[{String(i + 1).padStart(2, '0')}]</span>{line}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </div>

          {/* Close button at bottom */}
          <motion.button
            className="btn-neon w-full font-orbitron relative z-10 mt-4"
            style={{ background: 'rgba(0,245,255,0.1)' }}
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={() => setShowOptimizationResults(false)}
          >
            DISMISS
          </motion.button>

          {/* Animated accent line */}
          <motion.div
            className="absolute bottom-0 left-0 h-0.5"
            style={{ background: 'linear-gradient(90deg, transparent, #00f5ff, transparent)' }}
            animate={{ width: ['0%', '100%', '0%'] }}
            transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
