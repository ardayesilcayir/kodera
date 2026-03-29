'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePrismStore } from '@/lib/store';
import { FLEET_SATELLITES } from '@/lib/satellites';

const MISSION_OPTIONS = [
  { value: 'communication', label: 'COMM' },
  { value: 'observation', label: 'OBS' },
  { value: 'emergency', label: 'EMER' },
  { value: 'balanced', label: 'BAL' },
];

const OPT_MODE_OPTIONS = [
  { value: 'balanced', label: 'BALANCED' },
  { value: 'efficiency', label: 'EFFICIENCY' },
  { value: 'coverage', label: 'COVERAGE' },
  { value: 'speed', label: 'SPEED' },
];

export default function SatelliteListPanel() {
  const selectedFleetSatId = usePrismStore((s) => s.selectedFleetSatId);
  const selectFleetSat = usePrismStore((s) => s.selectFleetSat);
  const maneuverTarget = usePrismStore((s) => s.maneuverTarget);
  const setManeuverTarget = usePrismStore((s) => s.setManeuverTarget);
  const isManeuverRunning = usePrismStore((s) => s.isManeuverRunning);
  const runManeuver = usePrismStore((s) => s.runManeuver);

  const [missionType, setMissionType] = useState('balanced');
  const [optMode, setOptMode] = useState('balanced');
  const [maxHours, setMaxHours] = useState(48);
  const [radius, setRadius] = useState(200);

  const selectedSat = FLEET_SATELLITES.find((s) => s.id === selectedFleetSatId);

  const canOptimize = selectedFleetSatId && maneuverTarget && !isManeuverRunning;

  const handleOptimize = () => {
    if (!canOptimize) return;
    runManeuver({
      missionType,
      optimizationMode: optMode,
      maxTransferHours: maxHours,
      targetRadiusKm: radius,
    });
  };

  return (
    <motion.div
      className="glass-panel scanlines relative overflow-hidden select-none"
      style={{ width: '280px', padding: '32px 24px', maxHeight: '75vh', display: 'flex', flexDirection: 'column' }}
      initial={{ x: 60, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 1, delay: 0.5, ease: 'easeOut' }}
    >
      {/* HUD corners */}
      <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-cyan-400 opacity-70" />
      <div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-cyan-400 opacity-70" />
      <div className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-cyan-400 opacity-70" />
      <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-cyan-400 opacity-70" />

      {/* Icon */}
      <div className="flex justify-center mb-4 relative z-10">
        <motion.div
          className="w-12 h-12 rounded-full flex items-center justify-center"
          style={{ border: '1px solid rgba(0,245,255,0.4)', background: 'rgba(0,245,255,0.05)', boxShadow: '0 0 20px rgba(0,245,255,0.2)' }}
          animate={{ boxShadow: ['0 0 10px rgba(0,245,255,0.2)', '0 0 25px rgba(0,245,255,0.5)', '0 0 10px rgba(0,245,255,0.2)'] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00f5ff" strokeWidth="1.5">
            <rect x="4" y="4" width="6" height="6" rx="1" />
            <rect x="14" y="4" width="6" height="6" rx="1" />
            <rect x="4" y="14" width="6" height="6" rx="1" />
            <rect x="14" y="14" width="6" height="6" rx="1" />
          </svg>
        </motion.div>
      </div>

      {/* Title */}
      <div className="text-center mb-3 relative z-10">
        <span className="font-orbitron text-xs font-bold tracking-widest text-neon" style={{ fontSize: '11px', letterSpacing: '3px' }}>
          FLEET ASSETS
        </span>
      </div>

      {/* Divider */}
      <div className="w-full h-px mb-4 relative z-10" style={{ background: 'linear-gradient(90deg, transparent, rgba(0,245,255,0.4), transparent)' }} />

      {/* Scrollable content */}
      <div className="overflow-y-auto no-scrollbar flex-1 relative z-10">

        {/* Satellite list */}
        <div className="space-y-2 mb-4">
          {FLEET_SATELLITES.map((sat) => {
            const active = sat.id === selectedFleetSatId;
            return (
              <motion.button
                key={sat.id}
                className="w-full text-left p-2 rounded border transition-all"
                style={{
                  background: active ? 'rgba(0,245,255,0.08)' : 'rgba(0,10,20,0.5)',
                  borderColor: active ? 'rgba(0,245,255,0.5)' : 'rgba(0,245,255,0.1)',
                }}
                whileHover={{ borderColor: 'rgba(0,245,255,0.4)' }}
                onClick={() => selectFleetSat(active ? null : sat.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full" style={{ background: `#${sat.color.toString(16).padStart(6, '0')}` }} />
                    <span className="font-mono-tech text-[10px] text-[#00f5ff] font-bold">{sat.name}</span>
                  </div>
                  <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] uppercase">{sat.mission_type.slice(0, 4)}</span>
                </div>
                <div className="flex gap-3 mt-1">
                  <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.5)]">{sat.altitude_km}km</span>
                  <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.5)]">{sat.inclination_deg}°</span>
                </div>
              </motion.button>
            );
          })}
        </div>

        {/* Form — visible when satellite selected */}
        <AnimatePresence>
          {selectedSat && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              {/* Divider */}
              <div className="w-full h-px mb-3" style={{ background: 'linear-gradient(90deg, transparent, rgba(0,245,255,0.3), transparent)' }} />

              <div className="mb-1">
                <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] tracking-[3px] uppercase">TARGET</span>
              </div>

              {/* Target coordinates — editable */}
              <div className="space-y-2 mb-3">
                <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
                  <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">LAT</span>
                  <input
                    type="number"
                    value={maneuverTarget?.lat ?? ''}
                    placeholder="click earth"
                    onChange={(e) => {
                      const v = parseFloat(e.target.value);
                      if (!Number.isFinite(v)) return;
                      setManeuverTarget({ lat: Math.max(-90, Math.min(90, v)), lng: maneuverTarget?.lng ?? 0 });
                    }}
                    className="bg-transparent border-none font-mono-tech text-[10px] text-[#00f5ff] text-right outline-none w-24 tabular-nums placeholder:text-[rgba(0,245,255,0.25)]"
                    step={0.1}
                    min={-90}
                    max={90}
                  />
                </div>
                <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
                  <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">LON</span>
                  <input
                    type="number"
                    value={maneuverTarget?.lng ?? ''}
                    placeholder="—"
                    onChange={(e) => {
                      const v = parseFloat(e.target.value);
                      if (!Number.isFinite(v)) return;
                      setManeuverTarget({ lat: maneuverTarget?.lat ?? 0, lng: Math.max(-180, Math.min(180, v)) });
                    }}
                    className="bg-transparent border-none font-mono-tech text-[10px] text-[#00f5ff] text-right outline-none w-24 tabular-nums placeholder:text-[rgba(0,245,255,0.25)]"
                    step={0.1}
                    min={-180}
                    max={180}
                  />
                </div>
              </div>

              <div className="mb-1">
                <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] tracking-[3px] uppercase">PARAMETERS</span>
              </div>

              <div className="space-y-2 mb-4">
                {/* Mission type */}
                <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
                  <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">MISSION</span>
                  <select
                    value={missionType}
                    onChange={(e) => setMissionType(e.target.value)}
                    className="bg-transparent border-none font-mono-tech text-[10px] text-[#00f5ff] text-right outline-none cursor-pointer"
                  >
                    {MISSION_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value} className="bg-[#0a0f1a] text-[#00f5ff]">{o.label}</option>
                    ))}
                  </select>
                </div>
                {/* Optimization mode */}
                <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
                  <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">OPT_MODE</span>
                  <select
                    value={optMode}
                    onChange={(e) => setOptMode(e.target.value)}
                    className="bg-transparent border-none font-mono-tech text-[10px] text-[#00f5ff] text-right outline-none cursor-pointer"
                  >
                    {OPT_MODE_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value} className="bg-[#0a0f1a] text-[#00f5ff]">{o.label}</option>
                    ))}
                  </select>
                </div>
                {/* Radius */}
                <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
                  <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">RADIUS</span>
                  <input
                    type="number"
                    value={radius}
                    onChange={(e) => setRadius(Number(e.target.value))}
                    className="bg-transparent border-none font-mono-tech text-[10px] text-[#00f5ff] text-right outline-none w-16 tabular-nums"
                    min={50}
                    max={2000}
                  />
                </div>
                {/* Max transfer time */}
                <div className="flex justify-between items-center bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] p-2 rounded">
                  <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)]">MAX_TIME</span>
                  <div className="flex items-center gap-1">
                    <input
                      type="number"
                      value={maxHours}
                      onChange={(e) => setMaxHours(Number(e.target.value))}
                      className="bg-transparent border-none font-mono-tech text-[10px] text-[#00f5ff] text-right outline-none w-12 tabular-nums"
                      min={1}
                      max={168}
                    />
                    <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)]">h</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Action button */}
      {selectedSat && (
        <motion.button
          className="btn-neon w-full font-orbitron relative z-10 mt-4 disabled:opacity-40 disabled:cursor-wait disabled:pointer-events-none"
          style={{ background: canOptimize ? 'rgba(0,245,255,0.1)' : 'rgba(0,245,255,0.03)' }}
          whileHover={canOptimize ? { scale: 1.04 } : {}}
          whileTap={canOptimize ? { scale: 0.96 } : {}}
          onClick={handleOptimize}
          disabled={!canOptimize}
        >
          {isManeuverRunning ? 'CALCULATING...' : !maneuverTarget ? 'SELECT TARGET' : 'OPTIMIZE REPOSITION'}
        </motion.button>
      )}

      {/* Accent line */}
      <motion.div
        className="absolute bottom-0 left-0 h-0.5"
        style={{ background: 'linear-gradient(90deg, transparent, #00f5ff, transparent)' }}
        animate={{ width: ['0%', '100%', '0%'] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      />
    </motion.div>
  );
}
