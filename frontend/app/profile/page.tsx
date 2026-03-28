'use client';

import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function ProfilePage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <main style={{ width: '100vw', height: '100vh', backgroundColor: '#010409', color: '#e0f7ff', overflow: 'hidden', position: 'relative', display: 'flex', flexDirection: 'column', fontFamily: 'monospace' }}>
      
      {/* Background Gradient & CRT lines */}
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at center, #020b1a 0%, #010409 100%)', zIndex: 0 }} />
      <div style={{ position: 'absolute', inset: 0, backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.8) 2px, rgba(0,0,0,0.8) 4px)', opacity: 0.1, zIndex: 1, pointerEvents: 'none' }} />

      {/* Header Bar */}
      <header style={{ position: 'relative', zIndex: 10, padding: '24px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(0, 245, 255, 0.1)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <button 
            onClick={() => router.push('/')}
            style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'none', border: 'none', color: '#00f5ff', cursor: 'pointer', fontFamily: '"Orbitron", sans-serif', fontSize: '12px', letterSpacing: '0.2em' }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            RETURN TO COMMAND
          </button>
        </div>
        <div style={{ fontFamily: '"Orbitron", sans-serif', color: 'rgba(0, 245, 255, 0.5)', fontSize: '10px', letterSpacing: '0.3em' }}>
          NODE SECURE
        </div>
      </header>

      {/* Main Content */}
      <div style={{ relative: 'relative', zIndex: 10, flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '2rem' }}>
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          style={{ width: '100%', maxWidth: '800px', display: 'flex', gap: '40px' }}
        >
          {/* Left Column: Avatar & Rank */}
          <div style={{ width: '300px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            
            <div style={{ background: 'rgba(0, 10, 20, 0.6)', border: '1px solid rgba(0, 245, 255, 0.3)', borderRadius: '8px', padding: '32px', display: 'flex', flexDirection: 'column', alignItems: 'center', boxShadow: '0 0 30px rgba(0,245,255,0.05)' }}>
              
              {/* Avatar Ring */}
              <motion.div 
                style={{ width: '140px', height: '140px', borderRadius: '50%', border: '2px dashed rgba(0,245,255,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', marginBottom: '24px', position: 'relative' }}
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
              >
                <div style={{ width: '120px', height: '120px', borderRadius: '50%', background: 'rgba(0,245,255,0.1)', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                  <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#00f5ff" strokeWidth="1">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                </div>
              </motion.div>

              <h2 style={{ fontFamily: '"Orbitron", sans-serif', fontSize: '24px', letterSpacing: '0.15em', color: '#fff', margin: '0 0 8px 0' }}>GHOST-01</h2>
              <div style={{ color: '#00f5ff', fontSize: '12px', letterSpacing: '0.2em' }}>COMMANDER</div>

              <div style={{ width: '100%', height: '1px', background: 'linear-gradient(90deg, transparent, rgba(0,245,255,0.5), transparent)', margin: '24px 0' }}></div>

              <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'rgba(255,255,255,0.6)' }}>
                  <span>CLEARANCE</span> <span style={{ color: '#00ffcc' }}>LEVEL 5</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'rgba(255,255,255,0.6)' }}>
                  <span>DIVISION</span> <span style={{ color: '#e0f7ff' }}>ORBITAL RECON</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'rgba(255,255,255,0.6)' }}>
                  <span>STATUS</span> <span style={{ color: '#00f5ff' }}>ACTIVE</span>
                </div>
              </div>

            </div>

          </div>

          {/* Right Column: Stats & Logs */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '24px' }}>
            
            {/* Bio/Details */}
            <div style={{ flex: 1, background: 'rgba(0, 10, 20, 0.6)', border: '1px solid rgba(0, 245, 255, 0.1)', borderRadius: '8px', padding: '32px' }}>
              <h3 style={{ fontFamily: '"Orbitron", sans-serif', color: 'rgba(0, 245, 255, 0.7)', fontSize: '12px', letterSpacing: '0.2em', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '4px', height: '12px', background: '#00f5ff' }}></div> 
                SERVICE DOSSIER
              </h3>
              
              <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '13px', lineHeight: '1.8', letterSpacing: '0.05em' }}>
                Operator GHOST-01 has been an active participant in global satellite reconnaissance and orbital trajectory mapping since the inception of the PRISM Initiative. Expert in high-altitude interception and secure comms decryption.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '32px' }}>
                <div style={{ background: 'rgba(0,245,255,0.05)', border: '1px solid rgba(0,245,255,0.1)', padding: '16px', borderRadius: '4px' }}>
                  <div style={{ color: 'rgba(0,245,255,0.5)', fontSize: '9px', letterSpacing: '0.1em', marginBottom: '8px' }}>MISSIONS COMPLETED</div>
                  <div style={{ fontFamily: '"Orbitron", sans-serif', fontSize: '24px', color: '#fff' }}>1,204</div>
                </div>
                <div style={{ background: 'rgba(0,245,255,0.05)', border: '1px solid rgba(0,245,255,0.1)', padding: '16px', borderRadius: '4px' }}>
                  <div style={{ color: 'rgba(0,245,255,0.5)', fontSize: '9px', letterSpacing: '0.1em', marginBottom: '8px' }}>UPTIME LOGS</div>
                  <div style={{ fontFamily: '"Orbitron", sans-serif', fontSize: '24px', color: '#fff' }}>99.9%</div>
                </div>
                <div style={{ background: 'rgba(0,245,255,0.05)', border: '1px solid rgba(0,245,255,0.1)', padding: '16px', borderRadius: '4px' }}>
                  <div style={{ color: 'rgba(0,245,255,0.5)', fontSize: '9px', letterSpacing: '0.1em', marginBottom: '8px' }}>LAST LOGIN LOCATION</div>
                  <div style={{ fontFamily: '"Orbitron", sans-serif', fontSize: '14px', color: '#fff', marginTop: '6px' }}>SECURE SAT-V</div>
                </div>
                <div style={{ background: 'rgba(0,245,255,0.05)', border: '1px solid rgba(0,245,255,0.1)', padding: '16px', borderRadius: '4px' }}>
                  <div style={{ color: 'rgba(0,245,255,0.5)', fontSize: '9px', letterSpacing: '0.1em', marginBottom: '8px' }}>ENCRYPTION KEY</div>
                  <div style={{ fontFamily: '"Orbitron", sans-serif', fontSize: '14px', color: '#fff', marginTop: '6px' }}>RSA-4096-ACT</div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: '16px' }}>
              <button 
                onClick={() => router.push('/')}
                style={{ flex: 1, padding: '16px', background: 'rgba(0, 245, 255, 0.1)', border: '1px solid rgba(0, 245, 255, 0.4)', borderRadius: '4px', color: '#00f5ff', fontFamily: '"Orbitron", sans-serif', fontSize: '11px', letterSpacing: '0.2em', cursor: 'pointer', transition: 'all 0.3s' }}
              >
                RETURN TO DASHBOARD
              </button>
              <button 
                onClick={() => router.push('/login')}
                style={{ flex: 1, padding: '16px', background: 'rgba(255, 20, 147, 0.1)', border: '1px solid rgba(255, 20, 147, 0.4)', borderRadius: '4px', color: '#ff4da6', fontFamily: '"Orbitron", sans-serif', fontSize: '11px', letterSpacing: '0.2em', cursor: 'pointer', transition: 'all 0.3s' }}
              >
                DISCONNECT UPLINK
              </button>
            </div>

          </div>

        </motion.div>
      </div>

    </main>
  );
}
