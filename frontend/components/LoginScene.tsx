'use client';

import { useRef, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Sphere, Stars, useTexture } from '@react-three/drei';
import * as THREE from 'three';
import { EffectComposer, Bloom } from '@react-three/postprocessing';

export default function LoginScene() {
  const groupRef = useRef<THREE.Group>(null);
  
  const [dayMap, cloudsMap] = useTexture([
    'https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg',
    'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_clouds_1024.png',
  ]);

  useEffect(() => {
    dayMap.colorSpace = THREE.SRGBColorSpace;
  }, [dayMap]);

  useFrame((state, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.05;
      groupRef.current.rotation.x = 0.2; // Slight tilt
    }
  });

  return (
    <>
      <color attach="background" args={['#010409']} />
      <ambientLight intensity={0.5} color="#ffffff" />
      <directionalLight position={[8, 5, 5]} intensity={2.5} color="#ffffff" />
      <directionalLight position={[-5, -3, -5]} intensity={1.5} color="#00f5ff" />
      
      <Stars radius={100} depth={50} count={2000} factor={3} saturation={0} fade speed={1} />

      {/* Center massive Earth */}
      <group ref={groupRef} position={[0, -0.6, 0]}>
        
        {/* Core planet */}
        <Sphere args={[2.8, 64, 64]}>
          <meshStandardMaterial 
            map={dayMap}
            roughness={0.7}
            metalness={0.1}
          />
        </Sphere>
        
        {/* Cloud layer */}
        <Sphere args={[2.83, 64, 64]}>
          <meshStandardMaterial 
            map={cloudsMap}
            transparent
            opacity={0.6}
            blending={THREE.AdditiveBlending}
            depthWrite={false}
          />
        </Sphere>
        
        {/* Glowing Atmosphere edge */}
        <Sphere args={[2.92, 64, 64]}>
          <meshBasicMaterial 
            color="#00f5ff"
            transparent
            opacity={0.15}
            blending={THREE.AdditiveBlending}
            side={THREE.BackSide}
          />
        </Sphere>
      </group>

      <EffectComposer multisampling={8}>
        <Bloom intensity={0.6} luminanceThreshold={0.8} />
      </EffectComposer>
    </>
  );
}
