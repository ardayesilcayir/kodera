'use client';

import dynamic from 'next/dynamic';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePrismStore } from '@/lib/store';
import ProfilePanel from '@/components/ProfilePanel';
import StatusBar from '@/components/StatusBar';
import Header from '@/components/Header';
import CountryInfoPanel from '@/components/CountryInfoPanel';
import OptimizationHUD from '@/components/OptimizationHUD';
import SatelliteListPanel from '@/components/SatelliteListPanel';
import ManeuverResultsPanel from '@/components/ManeuverResultsPanel';

const Scene = dynamic(() => import('@/components/Scene'), {
  ssr: false,
  loading: () => (
    <div className="loading-screen w-full h-full flex items-center justify-center">
      <div className="text-center">
        <motion.div
          className="w-20 h-20 rounded-full mx-auto mb-6"
          style={{ border: '2px solid rgba(0,245,255,0.3)', borderTopColor: '#00f5ff' }}
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
        <div className="font-orbitron text-xs tracking-widest text-neon-dim" style={{ letterSpacing: '4px' }}>
          INITIALIZING SYSTEMS
        </div>
        <motion.div
          className="mt-2 font-mono-tech text-xs"
          style={{ color: 'rgba(0,245,255,0.3)' }}
          animate={{ opacity: [0.3, 1, 0.3] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          Loading orbital assets...
        </motion.div>
      </div>
    </div>
  ),
});

export default function Home() {
  const selectedCountry = usePrismStore((s) => s.selectedCountry);
  const setSelectedCountry = usePrismStore((s) => s.setSelectedCountry);
  const selectedFleetSatId = usePrismStore((s) => s.selectedFleetSatId);
  const isManeuverRunning = usePrismStore((s) => s.isManeuverRunning);
  const maneuverResult = usePrismStore((s) => s.maneuverResult);
  const maneuverError = usePrismStore((s) => s.maneuverError);
  const showOptimizationResults = usePrismStore((s) => s.showOptimizationResults);

  const [mounted, setMounted] = useState(false);
  const [showBoot, setShowBoot] = useState(true);

  useEffect(() => {
    setMounted(true);
    const timer = setTimeout(() => setShowBoot(false), 2200);
    return () => clearTimeout(timer);
  }, []);

  if (!mounted) return null;

  const maneuverActive = !!selectedFleetSatId;
  const showManeuverResults = isManeuverRunning || !!maneuverResult || !!maneuverError;

  return (
    <main
      className="relative w-screen h-screen overflow-hidden"
      style={{
        width: '100vw',
        height: '100vh',
        background: 'radial-gradient(ellipse at 50% 40%, #020b1a 0%, #010510 60%, #000308 100%)',
      }}
    >
      {/* Boot sequence overlay */}
      <AnimatePresence>
        {showBoot && (
          <motion.div
            className="absolute inset-0 z-50 flex flex-col items-center justify-center loading-screen"
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="font-mono-tech text-xs space-y-1 mb-8" style={{ color: 'rgba(0,245,255,0.6)' }}>
              {[
                '> INITIALIZING PRISM ORBIT COMMAND...',
                '> LOADING ORBITAL ASSET DATABASE...',
                '> CONNECTING TO GROUND STATIONS...',
                '> CALIBRATING EARTH SENSORS...',
                '> SYSTEM STATUS: NOMINAL',
              ].map((line, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.25 }}
                  style={{ fontSize: '11px' }}
                >
                  {line}
                </motion.div>
              ))}
            </div>
            <div className="w-64 h-0.5 rounded overflow-hidden" style={{ background: 'rgba(0,245,255,0.1)' }}>
              <motion.div
                className="h-full rounded"
                style={{ background: 'linear-gradient(90deg, #00f5ff, #00ffcc)' }}
                initial={{ width: '0%' }}
                animate={{ width: '100%' }}
                transition={{ duration: 1.8, ease: 'easeInOut' }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 3D Canvas */}
      <div className="absolute inset-0 z-0" style={{ width: '100%', height: '100%' }}>
        <Scene />
      </div>

      {/* Vignette */}
      <div className="absolute inset-0 z-1 pointer-events-none" style={{ background: 'radial-gradient(ellipse at center, transparent 40%, rgba(0,2,10,0.6) 100%)' }} />
      <div className="absolute inset-0 z-1 pointer-events-none opacity-5" style={{ backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.8) 2px, rgba(0,0,0,0.8) 4px)' }} />

      {/* Header */}
      <Header />

      {/* Left Panel: Profile */}
      <div className="absolute z-20" style={{ left: '3%', top: '50%', transform: 'translateY(-50%)' }}>
        <ProfilePanel />
      </div>

      {/* Bottom Status Bar */}
      <div className="absolute z-20" style={{ bottom: '24px', left: '4%', right: '4%' }}>
        <StatusBar />
      </div>

      {/* Center: CountryInfoPanel — only visible when no fleet satellite is selected */}
      {!maneuverActive && (
        <div className="absolute inset-0 z-30 pointer-events-none">
          <CountryInfoPanel
            country={selectedCountry}
            onClose={() => {
              setSelectedCountry(null);
              usePrismStore.getState().setSurfaceTarget(null);
              usePrismStore.getState().setCameraZoomed(false);
              usePrismStore.getState().setShowOptimizationResults(false);
              usePrismStore.getState().resetScan();
            }}
          />
        </div>
      )}

      {/* Right Panel: conditional */}
      <div className="absolute z-20" style={{ right: '3%', top: '50%', transform: 'translateY(-55%)' }}>
        <AnimatePresence mode="wait">
          {showManeuverResults ? (
            <ManeuverResultsPanel key="maneuver-results" />
          ) : showOptimizationResults && !maneuverActive ? (
            <OptimizationHUD key="optimization-hud" />
          ) : (
            <SatelliteListPanel key="satellite-list" />
          )}
        </AnimatePresence>
      </div>

      {/* HUD corner labels */}
      <motion.div className="absolute top-16 left-8 z-10 pointer-events-none" initial={{ opacity: 0 }} animate={{ opacity: 0.3 }} transition={{ delay: 2 }}>
        <div className="font-mono-tech" style={{ fontSize: '9px', color: '#00f5ff', letterSpacing: '4px' }}>GEOSPATIAL_DATA_LINK // SECURE</div>
        <div className="font-mono-tech" style={{ fontSize: '7px', color: '#00f5ff', letterSpacing: '2px', opacity: 0.5 }}>LATENCY: 14MS // STATUS: NOMINAL</div>
      </motion.div>

      <motion.div className="absolute top-16 right-8 z-10 pointer-events-none text-right" initial={{ opacity: 0 }} animate={{ opacity: 0.3 }} transition={{ delay: 2 }}>
        <div className="font-mono-tech" style={{ fontSize: '9px', color: '#00f5ff', letterSpacing: '4px' }}>ORBITAL_TRAJECTORY_MAPPING</div>
        <div className="font-mono-tech" style={{ fontSize: '7px', color: '#00f5ff', letterSpacing: '2px', opacity: 0.5 }}>AUTO_CORRECTION: ENABLED</div>
      </motion.div>

      <motion.div className="absolute bottom-32 left-8 z-10 pointer-events-none" initial={{ opacity: 0 }} animate={{ opacity: 0.2 }} transition={{ delay: 2.5 }}>
        <div className="font-mono-tech" style={{ fontSize: '9px', color: '#00f5ff', letterSpacing: '4px' }}>COMMUNICATION_RELAY_GRID</div>
        <div className="font-mono-tech" style={{ fontSize: '7px', color: '#00f5ff', letterSpacing: '2px' }}>UPLINK: ACTIVE // STATION: LEO-01</div>
      </motion.div>

      <motion.div className="absolute bottom-32 right-8 z-10 pointer-events-none text-right" initial={{ opacity: 0 }} animate={{ opacity: 0.2 }} transition={{ delay: 2.5 }}>
        <div className="font-mono-tech" style={{ fontSize: '9px', color: '#00f5ff', letterSpacing: '4px' }}>THERMAL_SENSING_ARRAYS</div>
        <div className="font-mono-tech" style={{ fontSize: '7px', color: '#00f5ff', letterSpacing: '2px' }}>SCAN_RATE: 0.8s // CALIBRATED</div>
      </motion.div>

      {/* Click hint */}
      <AnimatePresence>
        {!selectedCountry && !maneuverActive && (
          <motion.div
            className="absolute bottom-28 left-1/2 z-10 pointer-events-none"
            style={{ transform: 'translateX(-50%)' }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ delay: 3 }}
          >
            <motion.div
              className="font-mono-tech text-center"
              style={{ fontSize: '10px', color: 'rgba(0,245,255,0.3)', letterSpacing: '2px' }}
              animate={{ opacity: [0.3, 0.7, 0.3] }}
              transition={{ duration: 3, repeat: Infinity }}
            >
              DRAG TO ROTATE • CLICK EARTH TO SCAN REGION
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}
