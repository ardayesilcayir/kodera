'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('prism_token') || 'mock_token';
        const data = await api.getMe(token).catch(() => null);
        
        setUser(data || {
          operator_id: "GHOST-01",
          rank: "COMMANDER",
          clearance: "LEVEL 5 (ULTIMATUM)",
          division: "ORBITAL RECONNAISSANCE & STRATEGIC INTEL",
          status: "ACTIVE_DUTY",
          full_name: "ELARA VANCE",
          email: "e.vance@prism.command.mil",
          bio: "Expert in high-altitude interception and secure comms decryption. Lead developer of the PRISM AI Genesis engine. Multiple commendations for deep-space synchronization protocols.",
          stats: {
             missions_total: 1248,
             uplink_success_rate: "99.98%",
             active_satellites_controlled: 48,
             unauthorized_access_blocks: 42,
             last_uplink_node: "SECURE_SAT_V",
             network_latency: "14ms",
             encryption: "RSA-8192-PRIME"
          },
          service_history: [
            { id: 1, type: "UPLINK", date: "2026-03-29", detail: "Sector EU-WEST Synced", status: "SUCCESS" },
            { id: 2, type: "DEPLOY", date: "2026-03-28", detail: "Nova-6 Constellation Initialized", status: "SUCCESS" },
            { id: 3, type: "SECURITY", date: "2026-03-27", detail: "Deep-packet decryption test", status: "NEUTRAL" },
            { id: 4, type: "SYNC", date: "2026-03-26", detail: "Orbital drift correction (0.002ms)", status: "SUCCESS" }
          ]
        });
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (loading) return (
    <div className="min-h-screen bg-[#010409] flex items-center justify-center">
       <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-2 border-cyan-400/20 border-t-cyan-400 rounded-full animate-spin shadow-[0_0_20px_#00f5ff50]" />
          <div className="font-orbitron animate-pulse text-cyan-400 text-[10px] tracking-[5px]">UPLINKING_PROFILE_DATA...</div>
       </div>
    </div>
  );

  return (
    <main className="min-h-screen bg-[#010810] text-[#e0f7ff] overflow-x-hidden relative flex flex-col font-mono selection:bg-cyan-500/30">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_#020b1a_0%,_#010409_100%)] z-0" />
      <div className="absolute inset-0 bg-[repeating-linear-gradient(0deg,transparent,transparent_1px,rgba(0,0,0,0.5)_1px,rgba(0,0,0,0.5)_2px)] opacity-10 z-1 pointer-events-none" />
      <div className="absolute top-0 w-full h-px bg-gradient-to-r from-transparent via-cyan-400/30 to-transparent" />

      <header className="relative z-10 px-8 py-6 flex justify-between items-center border-b border-white/5 backdrop-blur-xl bg-black/40">
        <button 
          onClick={() => router.push('/')}
          className="flex items-center gap-3 bg-white/5 hover:bg-cyan-400/10 border border-white/10 hover:border-cyan-400/40 px-5 py-2.5 rounded-lg text-cyan-400 transition-all font-orbitron text-[11px] tracking-[2px] shadow-inner"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          RETURN TO COMMAND
        </button>
        <div className="flex flex-col items-end gap-1">
           <div className="font-orbitron text-white font-black text-[10px] tracking-[6px] opacity-60">ACCESS_LEVEL: {user?.clearance.split(' ')[1] || 'RESTRICTED'}</div>
           <div className="font-mono text-cyan-400/40 text-[8px] tracking-[3px] uppercase">Node: {user?.stats.last_uplink_node} // STATUS: STABLE</div>
        </div>
      </header>

      <div className="relative z-10 flex-1 flex flex-col items-center py-12 px-6 overflow-y-auto no-scrollbar">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-[1000px] grid grid-cols-1 lg:grid-cols-12 gap-8 items-start"
        >
          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="glass-panel p-8 rounded-2xl border border-white/10 relative overflow-hidden group">
               <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
               <div className="flex justify-center mb-8 relative">
                  <div className="w-40 h-40 rounded-full border border-cyan-400/30 p-2 relative">
                     <motion.div className="absolute inset-0 border-2 border-dashed border-cyan-400/20 rounded-full" animate={{ rotate: 360 }} transition={{ duration: 30, repeat: Infinity, ease: 'linear' }} />
                     <div className="w-full h-full rounded-full bg-cyan-400/5 flex items-center justify-center overflow-hidden">
                        <svg className="w-20 h-20 text-cyan-400/40" fill="none" stroke="currentColor" strokeWidth="0.8" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2.5M12 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" /></svg>
                     </div>
                  </div>
                  <div className="absolute bottom-2 right-12 w-4 h-4 rounded-full bg-[#00ffcc] shadow-[0_0_15px_#00ffcc] border-4 border-[#010810]" />
               </div>
               <div className="text-center mb-8">
                  <h2 className="font-orbitron text-2xl font-black text-white tracking-[4px] mb-2">{user?.operator_id}</h2>
                  <div className="text-cyan-400 font-black text-[11px] tracking-[6px] uppercase opacity-70">{user?.rank}</div>
               </div>
               <div className="space-y-4 pt-6 border-t border-white/5">
                  <div className="flex justify-between items-center group/item"><span className="text-[10px] text-white/30 tracking-[3px] uppercase">SECURITY</span><span className="text-[12px] font-bold text-[#00ffcc] tracking-tight">{user?.clearance.split(' ')[0]}</span></div>
                  <div className="flex justify-between items-center group/item"><span className="text-[10px] text-white/30 tracking-[3px] uppercase">STATUS</span><span className="text-[12px] font-bold text-white tracking-tight">{user?.status}</span></div>
                  <div className="pt-4"><div className="text-[9px] text-cyan-400/40 tracking-[5px] uppercase mb-4 text-center">ACCESS_RESTRICTION</div><div className="flex gap-2">{[...Array(5)].map((_, i) => (<div key={i} className={`flex-1 h-1.5 rounded-full ${i < 4 ? 'bg-cyan-400' : 'bg-white/10'}`} />))}</div></div>
               </div>
            </div>
          </div>
          <div className="lg:col-span-8 flex flex-col gap-8">
            <div className="glass-panel p-10 rounded-2xl border border-white/10 bg-black/60 shadow-2xl">
               <div className="flex items-center gap-6 mb-10"><div className="h-px flex-1 bg-gradient-to-r from-transparent via-cyan-400/20 to-cyan-400/50" /><h3 className="font-orbitron text-cyan-400 text-[13px] font-black tracking-[10px]">SERVICE_DOSSIER</h3><div className="h-px flex-1 bg-gradient-to-l from-transparent via-cyan-400/20 to-cyan-400/50" /></div>
               <div className="grid grid-cols-1 md:grid-cols-2 gap-10 mb-12">
                  <div className="space-y-6">
                     <div className="flex flex-col gap-2"><span className="text-[9px] text-cyan-400/50 tracking-[4px] uppercase decoration-cyan-400/20 underline-offset-8 mb-2">OPERATOR_IDENTITY</span><div className="text-xl font-black text-white">{user?.full_name}</div><div className="text-[12px] text-white/40">{user?.email}</div></div>
                     <div className="flex flex-col gap-2"><span className="text-[9px] text-cyan-400/50 tracking-[4px] uppercase decoration-cyan-400/20 underline-offset-8 mb-2">BIOMETRIC_PROFILE</span><p className="text-[13px] text-white/60 leading-relaxed font-light">{user?.bio}</p></div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">{[{ label: 'UPLINK_SUCCESS', value: user?.stats.uplink_success_rate, color: '#00ffcc' }, { label: 'MISSIONS', value: user?.stats.missions_total, color: '#fff' }, { label: 'ACTIVE_CONTROL', value: user?.stats.active_satellites_controlled, color: '#00f5ff' }, { label: 'BLOCK_COUNT', value: user?.stats.unauthorized_access_blocks, color: '#ff2d55' }].map((stat, i) => (<div key={i} className="glass-panel p-5 rounded-xl border border-white/5 bg-white/[0.02] active:scale-95 transition-all"><div className="text-[8px] text-white/30 tracking-[2px] uppercase mb-4">{stat.label}</div><div className="text-2xl font-black tabular-nums" style={{ color: stat.color }}>{stat.value}</div></div>))}</div>
               </div>
            </div>
            <div className="glass-panel p-10 rounded-2xl border border-white/10 bg-black/60 overflow-hidden relative">
               <h3 className="font-orbitron text-white text-[10px] font-black tracking-[8px] mb-8 flex items-center gap-4"><div className="w-1.5 h-6 bg-cyan-400 shadow-[0_0_15px_#00f5ff]" />MISSION_ACTIVITY_LOG</h3>
               <div className="space-y-4">
                  {user?.service_history.map((log: any, i: number) => (
                     <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }} key={log.id} className="flex items-center gap-6 p-4 rounded-xl border border-white/5 hover:bg-white/[0.03] transition-all group">
                        <div className="font-mono text-[10px] text-cyan-400/40 w-24 tabular-nums">{log.date}</div>
                        <div className={`w-2 h-2 rounded-full ${log.status === 'SUCCESS' ? 'bg-[#00ffcc]' : 'bg-orange-400 opacity-50'}`} />
                        <div className="flex-1">
                           <div className="text-[12px] font-bold text-white/80 group-hover:text-white transition-colors uppercase tracking-widest">{log.detail}</div>
                           <div className="text-[8px] text-white/20 uppercase tracking-[2px]">{log.type}</div>
                        </div>
                     </motion.div>
                  ))}
               </div>
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
