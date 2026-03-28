'use client';

import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Points } from '@react-three/drei';

export default function Starfield() {
  const starsRef = useRef<THREE.Points>(null);
  const count = 8000;

  const [positions, colors] = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      // Spherical distribution
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 80 + Math.random() * 40;

      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);

      // Color variation: white, blue-white, slight cyan
      const brightness = 0.6 + Math.random() * 0.4;
      const blueTint = Math.random() > 0.8;
      const cyanTint = Math.random() > 0.95;

      col[i * 3] = brightness * (blueTint ? 0.8 : 1.0);
      col[i * 3 + 1] = brightness * (cyanTint ? 1.0 : (blueTint ? 0.9 : 1.0));
      col[i * 3 + 2] = brightness * (blueTint ? 1.0 : (cyanTint ? 1.0 : 0.95));
    }

    return [pos, col];
  }, []);

  // Very slow parallax rotation
  useFrame((_, delta) => {
    if (starsRef.current) {
      starsRef.current.rotation.y += delta * 0.005;
      starsRef.current.rotation.x += delta * 0.002;
    }
  });

  return (
    <points ref={starsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
        <bufferAttribute
          attach="attributes-color"
          args={[colors, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.15}
        vertexColors
        transparent
        opacity={0.9}
        sizeAttenuation
        depthWrite={false}
      />
    </points>
  );
}

// Nebula/galaxy background (large plane particles)
export function NebulaBackground() {
  const nebulaRef = useRef<THREE.Points>(null);
  const count = 2000;

  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      // Milky Way band distribution
      const theta = Math.random() * Math.PI * 2;
      const spread = (Math.random() - 0.5) * 0.3;
      const phi = Math.PI / 2 + spread + (Math.random() - 0.5) * 0.5;
      const r = 70 + Math.random() * 30;

      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);
    }
    return pos;
  }, []);

  useFrame((_, delta) => {
    if (nebulaRef.current) {
      nebulaRef.current.rotation.y += delta * 0.003;
    }
  });

  return (
    <points ref={nebulaRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.4}
        color={new THREE.Color(0x334488)}
        transparent
        opacity={0.15}
        sizeAttenuation
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}
