'use client';

import { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import LoginScene from '@/components/LoginScene';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const router = useRouter();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    router.push('/'); 
  };

  return (
    <main style={{ width: '100vw', height: '100vh', overflow: 'hidden', backgroundColor: '#010409', position: 'relative', display: 'flex', flexDirection: 'column', fontFamily: 'monospace' }}>
      
      {/* 3D Background */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, width: '100%', height: '100%', zIndex: 0, pointerEvents: 'none' }}>
        <Canvas camera={{ position: [0, 0, 6], fov: 45 }}>
          <LoginScene />
        </Canvas>
      </div>

      {/* Overlay darkening layer for better UI contrast */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, zIndex: 1, pointerEvents: 'none', background: 'linear-gradient(to bottom, rgba(0,0,0,0.6) 0%, transparent 50%, rgba(0,0,0,0.8) 100%)' }}></div>

      {/* HUD Corners */}
      <div style={{ position: 'absolute', top: '24px', left: '32px', zIndex: 20, pointerEvents: 'none' }}>
        <div style={{ color: '#00f5ff', fontWeight: 'bold', letterSpacing: '0.2em', fontSize: '10px' }}>
          SYSTEM STATUS: <span style={{ color: '#00ffcc', textShadow: '0 0 8px rgba(0,245,255,0.8)' }}>NOMINAL</span>
        </div>
      </div>
      
      <div style={{ position: 'absolute', top: '24px', right: '32px', zIndex: 20, pointerEvents: 'none' }}>
        <div style={{ color: 'rgba(0, 245, 255, 0.8)', fontWeight: '500', letterSpacing: '0.2em', fontSize: '8px' }}>
          ORBITAL COORDINATES: <span style={{ color: '#00f5ff' }}>28.5728° N, 80.6490° W</span>
        </div>
      </div>

      <div style={{ position: 'absolute', bottom: '24px', left: '32px', zIndex: 20, pointerEvents: 'none' }}>
        <div style={{ color: 'rgba(0, 150, 200, 0.8)', fontWeight: '500', letterSpacing: '0.2em', fontSize: '8px', textTransform: 'uppercase' }}>
          © 2024 PRISM COMMAND. MISSION STATUS: <span style={{ color: '#00f5ff' }}>READY</span>
        </div>
      </div>

      <div style={{ position: 'absolute', bottom: '24px', right: '32px', zIndex: 20, display: 'flex', alignItems: 'center', gap: '24px', fontSize: '8px', letterSpacing: '0.3em', color: 'rgba(0, 245, 255, 0.6)', fontWeight: '500' }}>
        <button style={{ background: 'none', border: 'none', color: 'inherit', letterSpacing: 'inherit', cursor: 'pointer' }}>TELEMETRY</button>
        <button style={{ background: 'none', border: 'none', color: 'inherit', letterSpacing: 'inherit', cursor: 'pointer' }}>SYSTEMS</button>
        <button style={{ background: 'none', border: 'none', color: 'inherit', letterSpacing: 'inherit', cursor: 'pointer' }}>PROTOCOLS</button>
      </div>

      {/* Central Content */}
      <div style={{ position: 'relative', zIndex: 10, flex: 1, width: '100%', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
        
        {/* Auth Glass Panel */}
        <motion.div 
          className="relative z-10 pointer-events-auto"
          style={{ 
            width: '100%',
            maxWidth: '380px',
            background: 'rgba(2, 6, 12, 0.55)', 
            backdropFilter: 'blur(24px)',
            WebkitBackdropFilter: 'blur(24px)',
            border: '1px solid rgba(0, 245, 255, 0.15)',
            borderTop: '1px solid rgba(0, 245, 255, 0.4)',
            borderRadius: '12px',
            boxShadow: '0 25px 50px rgba(0,0,0,0.8), inset 0 1px 2px rgba(255,255,255,0.1), 0 0 40px rgba(0,245,255,0.05)',
            padding: '32px'
          }}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.0, ease: "easeOut", delay: 0.1 }}
        >
          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            
            <AnimatePresence mode="popLayout">
              {isLogin ? (
                <motion.div key="login" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                   <input type="text" required placeholder="OPERATOR ID" style={{ width: '100%', background: 'transparent', border: 'none', borderBottom: '1px solid rgba(0, 245, 255, 0.5)', padding: '10px 4px', color: '#00f5ff', fontSize: '13px', fontFamily: 'monospace', letterSpacing: '0.2em', outline: 'none', textShadow: '0 0 5px rgba(0,245,255,0.5)' }} />
                   <input type="password" required placeholder="SECURITY KEY" style={{ width: '100%', background: 'transparent', border: 'none', borderBottom: '1px solid rgba(0, 245, 255, 0.5)', padding: '10px 4px', color: '#00f5ff', fontSize: '13px', fontFamily: 'monospace', letterSpacing: '0.5em', outline: 'none', textShadow: '0 0 5px rgba(0,245,255,0.5)' }} />
                </motion.div>
              ) : (
                <motion.div key="register" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                   <input type="text" required placeholder="NEW OPERATOR ID" style={{ width: '100%', background: 'transparent', border: 'none', borderBottom: '1px solid rgba(255, 20, 147, 0.5)', padding: '10px 4px', color: '#ff4da6', fontSize: '13px', fontFamily: 'monospace', letterSpacing: '0.2em', outline: 'none', textShadow: '0 0 5px rgba(255,20,147,0.5)' }} />
                   <input type="email" required placeholder="SECURE COMMS EMAIL" style={{ width: '100%', background: 'transparent', border: 'none', borderBottom: '1px solid rgba(255, 20, 147, 0.5)', padding: '10px 4px', color: '#ff4da6', fontSize: '13px', fontFamily: 'monospace', letterSpacing: '0.2em', outline: 'none', textShadow: '0 0 5px rgba(255,20,147,0.5)' }} />
                   <input type="password" required placeholder="CREATE CYPHER KEY" style={{ width: '100%', background: 'transparent', border: 'none', borderBottom: '1px solid rgba(255, 20, 147, 0.5)', padding: '10px 4px', color: '#ff4da6', fontSize: '13px', fontFamily: 'monospace', letterSpacing: '0.5em', outline: 'none', textShadow: '0 0 5px rgba(255,20,147,0.5)' }} />
                </motion.div>
              )}
            </AnimatePresence>

            <motion.button 
              type="submit" 
              className="font-orbitron"
              animate={{ boxShadow: isLogin ? ['0 0 10px rgba(0,245,255,0.4)', '0 0 30px rgba(0,245,255,0.8)', '0 0 10px rgba(0,245,255,0.4)'] : ['0 0 10px rgba(255,20,147,0.4)', '0 0 30px rgba(255,20,147,0.8)', '0 0 10px rgba(255,20,147,0.4)'] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
              style={{ width: '100%', padding: '18px 0', marginTop: '16px', borderRadius: '4px', fontWeight: 'bold', fontSize: '12px', letterSpacing: '0.3em', color: '#010510', background: isLogin ? '#00f5ff' : '#ff4da6', border: 'none', cursor: 'pointer' }}
            >
              {isLogin ? "ESTABLISH CONNECTION" : "REGISTER PROTOCOL"}
            </motion.button>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: isLogin ? '#00e5ff' : '#ff4da6', boxShadow: isLogin ? '0 0 10px #00e5ff, 0 0 20px #00e5ff' : '0 0 10px #ff4da6, 0 0 20px #ff4da6' }}></div>
                <span style={{ fontSize: '8px', fontFamily: 'monospace', letterSpacing: '0.2em', textTransform: 'uppercase', color: isLogin ? 'rgba(0, 245, 255, 0.7)' : 'rgba(255, 20, 147, 0.7)' }}>
                  {isLogin ? "INITIATING UPLINK PROTOCOL..." : "AWAITING REGISTRY VERIFICATION..."}
                </span>
              </div>
              <div style={{ width: '128px', height: '1px', background: isLogin ? 'linear-gradient(to right, transparent, rgba(0,245,255,0.7), transparent)' : 'linear-gradient(to right, transparent, rgba(255,20,147,0.7), transparent)' }}></div>
            </div>

            <div style={{ textAlign: 'center', marginTop: '4px' }}>
              <button type="button" onClick={() => setIsLogin(!isLogin)} style={{ fontSize: '9px', letterSpacing: '0.1em', fontFamily: 'monospace', background: 'none', border: 'none', cursor: 'pointer', color: isLogin ? 'rgba(0,245,255,0.8)' : 'rgba(255,20,147,0.8)' }}>
                {isLogin ? "- CREATE NEW OPERATOR ID -" : "- RETURN TO SECURE AUTH -"}
              </button>
            </div>
            
          </form>
        </motion.div>

        {/* Data Row underneath the glass panel */}
        <div style={{ marginTop: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '32px', pointerEvents: 'none' }}>
           <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
             <span className="font-orbitron" style={{ color: 'rgba(0,245,255,0.4)', fontSize: '9px', letterSpacing: '0.15em', marginBottom: '4px' }}>SYNC RATE</span>
             <span style={{ color: '#e0f7ff', fontSize: '12px', letterSpacing: '0.05em', fontWeight: '500' }}>99.8%</span>
           </div>
           <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
             <span className="font-orbitron" style={{ color: 'rgba(0,245,255,0.4)', fontSize: '9px', letterSpacing: '0.15em', marginBottom: '4px' }}>LATENCY</span>
             <span style={{ color: '#e0f7ff', fontSize: '12px', letterSpacing: '0.05em', fontWeight: '500' }}>14ms</span>
           </div>
           <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
             <span className="font-orbitron" style={{ color: 'rgba(0,245,255,0.4)', fontSize: '9px', letterSpacing: '0.15em', marginBottom: '4px' }}>ENCRYPTION</span>
             <span style={{ color: '#e0f7ff', fontSize: '12px', letterSpacing: '0.05em', fontWeight: '500' }}>AES-512</span>
           </div>
           <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
             <span className="font-orbitron" style={{ color: 'rgba(0,245,255,0.4)', fontSize: '9px', letterSpacing: '0.15em', marginBottom: '4px' }}>NODE</span>
             <span style={{ color: '#e0f7ff', fontSize: '12px', letterSpacing: '0.05em', fontWeight: '500' }}>SAT-V</span>
           </div>
        </div>

      </div>
      
    </main>
  );
}
