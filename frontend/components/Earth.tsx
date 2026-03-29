'use client';

import React, { useRef, useMemo, useCallback } from 'react';
import { useFrame } from '@react-three/fiber';
import { useTexture, Sphere } from '@react-three/drei';
import * as THREE from 'three';
import { usePrismStore } from '@/lib/store';
import { pointToLatLng } from '@/lib/countryDetection';
import { EARTH_ROTATION_RAD_S, VISUAL_TIME_SCALE } from '@/lib/walkerOrbit';

// Enhanced Atmosphere Shaders
const atmosphereVertexShader = `
varying vec3 vNormal;
varying vec3 vPosition;
void main() {
  vNormal = normalize(normalMatrix * normal);
  vPosition = position;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const atmosphereFragmentShader = `
uniform float intensity;
uniform vec3 glowColor;
varying vec3 vNormal;
void main() {
  float rim = 1.0 - max(dot(vNormal, vec3(0.0, 0.0, 1.0)), 0.0);
  float alpha = pow(rim, 4.0) * intensity;
  gl_FragColor = vec4(glowColor, alpha);
}
`;

// Earth Surface Terminator Shader (Day/Night Blending)
const earthVertexShader = `
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vPosition;
void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);
  vPosition = (modelMatrix * vec4(position, 1.0)).xyz;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const earthFragmentShader = `
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vPosition;

uniform sampler2D dayMap;
uniform sampler2D nightMap;
uniform sampler2D cloudMap;
uniform vec3 sunDirection;

void main() {
  vec3 dayColor = texture2D(dayMap, vUv).rgb;
  vec3 nightColor = texture2D(nightMap, vUv).rgb;
  vec3 clouds = texture2D(cloudMap, vUv).rgb;
  
  // Calculate light intensity
  float intensity = dot(normalize(vNormal), normalize(sunDirection));
  
  // Smoothly blend day and night at the terminator
  float mixAmount = smoothstep(-0.1, 0.1, intensity);
  
  // Add highlight to clouds in day area
  vec3 color = mix(nightColor, dayColor + clouds * 0.3, mixAmount);
  
  gl_FragColor = vec4(color, 1.0);
}
`;

interface EarthProps {
  onCountryClick: (e: any) => void;
}

function RegionHighlight({ country }: { country: any }) {
  const pingerRef = useRef<THREE.Mesh>(null);
  
  useFrame((state) => {
    if (pingerRef.current) {
      const t = (state.clock.elapsedTime * 1.5) % 2.0; 
      pingerRef.current.scale.setScalar(t * 1.5);
      const mat = pingerRef.current.material as THREE.MeshBasicMaterial;
      mat.opacity = Math.max(0, 1.0 - t / 1.5);
    }
  });

  if (!country) return null;

  // Conversion: Sphere Geometry to Lat/Long (Precise)
  const latRad = country.lat * (Math.PI / 180);
  const lngRad = country.lng * (Math.PI / 180);
  
  const y = Math.sin(latRad);
  const x = -Math.cos(latRad) * Math.sin(lngRad);
  const z = -Math.cos(latRad) * Math.cos(lngRad);
  
  const pos = new THREE.Vector3(x, y, z).multiplyScalar(1.01);

  return (
    <group position={pos}>
      <mesh ref={pingerRef}>
        <ringGeometry args={[0.02, 0.025, 32]} />
        <meshBasicMaterial color={0x00f5ff} transparent opacity={0.8} depthWrite={false} blending={THREE.AdditiveBlending} />
      </mesh>
      <mesh>
        <sphereGeometry args={[0.008, 16, 16]} />
        <meshBasicMaterial color={0xffffff} />
      </mesh>
    </group>
  );
}




export default function Earth({ onCountryClick }: EarthProps) {
  const earthRef = useRef<THREE.Mesh>(null);
  const setEarthHovered = usePrismStore((s) => s.setEarthHovered);
  const selectedCountry = usePrismStore((s) => s.selectedCountry);
  const isEarthDragging = usePrismStore((s) => s.isEarthDragging);
  const simulationSpeedMultiplier = usePrismStore((s) => s.simulationSpeedMultiplier);
  
  // High-Res Cinematic Textures
  const [dayTexture, nightTexture, cloudTexture] = useTexture([
    'https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg',
    'https://unpkg.com/three-globe/example/img/earth-night.jpg',
    'https://unpkg.com/three-globe/example/img/earth-topology.png'
  ]);

  const earthMaterial = useMemo(() => {
    return new THREE.ShaderMaterial({
      uniforms: {
        dayMap: { value: dayTexture },
        nightMap: { value: nightTexture },
        cloudMap: { value: cloudTexture },
        sunDirection: { value: new THREE.Vector3(5, 3, 5) }
      },
      vertexShader: earthVertexShader,
      fragmentShader: earthFragmentShader
    });
  }, [dayTexture, nightTexture, cloudTexture]);

  const atmosphereMaterial = useMemo(() => {
    return new THREE.ShaderMaterial({
      vertexShader: atmosphereVertexShader,
      fragmentShader: atmosphereFragmentShader,
      uniforms: {
        intensity: { value: 0.6 },
        glowColor: { value: new THREE.Color(0x00d2ff) } // Neon Blue from spec
      },
      side: THREE.BackSide,
      blending: THREE.AdditiveBlending,
      transparent: true,
      depthWrite: false
    });
  }, []);

  useFrame((_, delta) => {
    if (!earthRef.current || selectedCountry) return;

    if (!isEarthDragging) {
      earthRef.current.rotateY(delta * EARTH_ROTATION_RAD_S * VISUAL_TIME_SCALE * simulationSpeedMultiplier);
    }
  });

  const handleInteraction = useCallback((e: any) => {
    e.stopPropagation();
    if (!e.point) return;

    // Direct Raycaster Point to Lat/Long (Precise Geometric Translation)
    const localPoint = e.point.clone();
    if (earthRef.current) {
        earthRef.current.worldToLocal(localPoint);
    }
    const normalized = localPoint.normalize();
    
    // Use the library's precision mapping
    const { lat, lng } = pointToLatLng(normalized.x, normalized.y, normalized.z);

    onCountryClick({ lat, lng, point: e.point });
  }, [onCountryClick]);

  return (
    <group>
      {/* Glow Haze Atmosphere Shell */}
      <Sphere args={[1.05, 64, 64]}>
        <primitive object={atmosphereMaterial} attach="material" />
      </Sphere>

      {/* Main Cinematic Earth */}
      <Sphere 
        ref={earthRef} 
        args={[1, 64, 64]} 
        onClick={handleInteraction}
        onPointerOver={() => setEarthHovered(true)}
        onPointerOut={() => setEarthHovered(false)}
      >
        <primitive object={earthMaterial} attach="material" />
        <RegionHighlight country={selectedCountry} />
      </Sphere>
    </group>
  );
}
