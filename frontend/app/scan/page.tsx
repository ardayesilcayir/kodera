'use client';

import dynamic from 'next/dynamic';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { usePrismStore } from '@/lib/store';
import Header from '@/components/Header';
import StatusBar from '@/components/StatusBar';

// Full-screen 3D world integration
const Scene = dynamic(() => import('@/components/Scene'), {
  ssr: false,
});

// Elite Sub-module for Information
function TacticalBox({ title, children, side = 'left' }: { title: string, children: React.ReactNode, side?: 'left'|'right' }) {
  return (
    <div className={`glass-panel scanlines p-6 border border-white/5 relative overflow-hidden mb-4 shadow-[0_20px_50px_rgba(0,0,0,0.5)] bg-black/20 ${side === 'right' ? 'text-right' : ''}`}>
       <div className={`font-orbitron text-[8px] text-cyan-400 tracking-[6px] opacity-40 uppercase mb-5 ${side === 'right' ? 'flex justify-end' : ''}`}>
         {side === 'left' && <span className="mr-2">▶</span>} {title} {side === 'right' && <span className="ml-2">◀</span>}
       </div>
       <div className="space-y-3">{children}</div>
       {/* Corner Accents */}
       <div className={`absolute top-0 ${side === 'left' ? 'left-0' : 'right-0'} w-2 h-2 border-t border-${side === 'left' ? 'l' : 'r'} border-cyan-400/30`} />
       <div className={`absolute bottom-0 ${side === 'left' ? 'right-0' : 'left-0'} w-2 h-2 border-b border-${side === 'left' ? 'r' : 'l'} border-cyan-400/10`} />
    </div>
  );
}

function DataRow({ label, value, color = "white", side = 'left' }: { label: string, value: string, color?: string, side?: 'left'|'right' }) {
  return (
    <div className={`flex ${side === 'right' ? 'flex-row-reverse' : 'flex-row'} justify-between items-center group py-1`}>
       <span className="font-mono-tech text-[7px] text-white/20 tracking-[3px] uppercase group-hover:text-cyan-400 transition-colors">{label}</span>
       <span className={`font-orbitron font-bold tracking-tighter text-[13px]`} style={{ color }}>{value}</span>
    </div>
  );
}

export default function ScanPage() {
  const router = useRouter();
  const { selectedCountry, scanResult, scanError, resetScan } = usePrismStore();
  const [progress, setProgress] = useState(0);
  const [mounted, setMounted] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    setMounted(true);
    const interval = setInterval(() => {
      setProgress(p => p < 100 ? p + 0.4 : 100);
    }, 45);

    const logGen = setInterval(() => {
       const codes = ['SYN', 'ACK', 'REV', 'STB', 'UPL'];
       const newLog = `[${new Date().toLocaleTimeString()}] ${codes[Math.floor(Math.random()*5)]}_LOG: 0x${Math.random().toString(16).slice(2,6).toUpperCase()} // OK`;
       setLogs(prev => [...prev.slice(-8), newLog]);
    }, 600);

    return () => {
       clearInterval(interval);
       clearInterval(logGen);
       resetScan();
    };
  }, []);

  if (!mounted) return null;

  return (
    <div className="fixed inset-0 w-full h-full overflow-hidden bg-black font-orbitron select-none">
      
      {/* 🚀 1. DEEP WORLD BACKGROUND (The Cinematic Core) */}
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ width: '100vw', height: '100vh', overflow: 'hidden' }}>
         <Scene />
         <div className="absolute inset-0 bg-black/40" />
         <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.9)_100%)]" />
      </div>

      {/* 🚀 2. DASHBOARD ARCHITECTURE (MATCHING MAIN DASHBOARD EXACTLY) */}
      {/* Header at Top (Spaced) */}
      <div className="absolute top-10 left-0 right-0 z-50">
         <Header />
      </div>
      
      {/* StatusBar at Bottom (Match dashboard bottom value) */}
      <div className="absolute bottom-10 left-[4%] right-[4%] z-50">
         <StatusBar />
      </div>

      {/* 🚀 3. TACTICAL INFORMATION HUB (Symmetric Sides) */}
      <div className="absolute left-[3%] top-1/2 -translate-y-1/2 z-40 w-[280px]">
         <motion.div initial={{ x: -60, opacity: 0 }} animate={{ x: 0, opacity: 1 }}>
            <TacticalBox title="SECTOR_PROFILE">
               <div className="mb-4">
                  <h2 className="text-2xl font-black text-white tracking-widest uppercase truncate">{scanResult?.constellation_name || selectedCountry?.name || 'GLOBAL'}</h2>
                  <div className="font-mono-tech text-[9px] text-cyan-400/40 uppercase tracking-[4px]">{scanResult?.region_id || selectedCountry?.region || 'International_Waters'}</div>
               </div>
               <DataRow label="Target_Type" value={scanResult?.mission_type || "STRATEGIC"} color="#00ffcc" />
               <DataRow label="Status" value={scanError ? "OFFLINE" : "SECURE"} />
            </TacticalBox>
            <TacticalBox title="GEOSPATIAL">
               <DataRow label="Latitude" value={`${selectedCountry?.lat.toFixed(4) || '0.000'}°`} />
               <DataRow label="Longitude" value={`${selectedCountry?.lng.toFixed(4) || '0.000'}°`} />
            </TacticalBox>
         </motion.div>
      </div>

      <div className="absolute right-[3%] top-1/2 -translate-y-1/2 z-40 w-[280px]">
         <motion.div initial={{ x: 60, opacity: 0 }} animate={{ x: 0, opacity: 1 }}>
            <TacticalBox title="SCAN_PROGRESS" side="right">
               <div className="mb-4 text-right">
                  <div className="text-6xl font-black text-white tabular-nums tracking-tighter shadow-cyan-400/20 drop-shadow-[0_0_15px_rgba(0,245,255,0.4)]">
                     {scanResult ? 100 : Math.floor(progress)}<span className="text-xl opacity-20 ml-1">%</span>
                  </div>
               </div>
               <div className="h-1 w-full bg-white/10 mt-4 rounded-full overflow-hidden">
                  <motion.div className="h-full bg-cyan-400" initial={{ width: 0 }} animate={{ width: scanResult ? '100%' : `${progress}%` }} />
               </div>
            </TacticalBox>
            <TacticalBox title="ORBIT_DATA" side="right">
               <DataRow label="Asset_Count" value={scanResult?.satellites?.length || '48'} side="right" />
               <DataRow label="Orbit_Family" value={scanResult?.optimization?.allowed_orbit_families?.[0] || 'LEO'} color="#00ffcc" side="right" />
            </TacticalBox>
         </motion.div>
      </div>

      {/* 🚀 4. TERMINATE BUTTON (Moved Above StatusBar but at the bottom) */}
      <button 
        onClick={() => {
           resetScan();
           router.push('/');
        }} 
        className="absolute bottom-28 left-1/2 -translate-x-1/2 z-50 text-[9px] tracking-[6px] text-white/30 hover:text-white transition-colors uppercase border-b border-white/5 pb-1"
      >
         Terminate_All_Uplinks
      </button>

      {/* 🚀 5. CONSOLE LOGS & ERRORS HUD */}
      <div className="absolute bottom-[160px] left-1/2 -translate-x-1/2 z-10 pointer-events-none opacity-20 font-mono-tech text-[7px] text-cyan-400 text-center w-[400px]">
         {scanError ? (
            <div className="text-red-500 font-bold bg-red-950/20 py-2 border border-red-500/30 animate-pulse">
               CRITICAL_FAILURE: {scanError.toUpperCase()}
            </div>
         ) : (
            <AnimatePresence mode="popLayout">
               {logs.map((log, i) => (
                  <motion.div key={log + i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                     {log}
                  </motion.div>
               ))}
            </AnimatePresence>
         )}
      </div>

    </div>
  );
}
