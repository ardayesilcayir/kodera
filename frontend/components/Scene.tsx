'use client';

import { Suspense, useRef, useCallback, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Stars } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import * as THREE from 'three';
import Earth from './Earth';
import OrbitalSystem from './OrbitalSystem';
import { usePrismStore } from '@/lib/store';
import { detectCountry } from '@/lib/countryDetection';

function SceneContent() {
  const { setSelectedCountry, setCameraZoomed, selectedCountry, isEarthDragging } = usePrismStore();
  const earthRef = useRef<THREE.Group>(null);
  const controlsRef = useRef<any>(null);

  // Centered composition for a balanced dashboard view
  const ASYMMETRY_OFFSET = 0;

  const handleCountryClick = useCallback((e: any) => {
    const lat = e.lat;
    const lng = e.lng;
    
    // Find country based on calculated lat/lng
    const country = detectCountry(lat, lng);
    setSelectedCountry(country);
    setCameraZoomed(true);
  }, [setSelectedCountry, setCameraZoomed]);

  useFrame((state, delta) => {
    // Intentional empty frame for future camera/composition overrides if needed
  });

  return (
    <>
      <ambientLight intensity={0.5} color={0x131315} />
      <directionalLight position={[5, 3, 5]} intensity={3.5} color={0xfff5e0} />
      <pointLight position={[-10, -5, -5]} intensity={1.5} color={0x0044ff} />

      <Stars radius={300} depth={60} count={20000} factor={7} saturation={0} fade speed={1} />

      {/* Global Centered Group - Reduced further for ultimate elegance */}
      <group ref={earthRef} position={[ASYMMETRY_OFFSET, -0.1, 0]} scale={1.4}>
         <Earth onCountryClick={handleCountryClick} />
         <OrbitalSystem />
      </group>

      <OrbitControls 
        ref={controlsRef}
        enablePan={false}
        enableRotate={!selectedCountry} 
        enableZoom={true}
        minDistance={3.2}
        maxDistance={12}
        enableDamping={true}
        dampingFactor={0.05}
        rotateSpeed={0.5}
      />

      <EffectComposer multisampling={8}>
        <Bloom intensity={0.8} luminanceThreshold={0.9} mipmapBlur />
      </EffectComposer>
    </>
  );
}

export default function Scene() {
  return (
    <Canvas
      camera={{ position: [0, 0, 6], fov: 40 }}
      gl={{
        antialias: true,
        toneMapping: THREE.ACESFilmicToneMapping,
        toneMappingExposure: 1.2,
      }}
      style={{ width: '100%', height: '100%', background: '#131315' }}
    >
      <Suspense fallback={null}>
        <SceneContent />
      </Suspense>
    </Canvas>
  );
}
