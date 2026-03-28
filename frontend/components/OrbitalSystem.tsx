'use client';

import { useRef, useMemo, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Line } from '@react-three/drei';
import { usePrismStore } from '@/lib/store';

// Orbital ring component
function OrbitalRing({ radius, tilt, speed, color, opacity }: {
  radius: number;
  tilt: number;
  speed: number;
  color: string;
  opacity: number;
}) {
  const groupRef = useRef<THREE.Group>(null);

  const points = useMemo(() => {
    const pts = [];
    for (let i = 0; i <= 128; i++) {
      const angle = (i / 128) * Math.PI * 2;
      pts.push(new THREE.Vector3(Math.cos(angle) * radius, 0, Math.sin(angle) * radius));
    }
    return pts;
  }, [radius]);

  useFrame((_, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * speed * 0.1;
    }
  });

  return (
    <group ref={groupRef} rotation={[tilt, 0, 0]}>
      <Line
        points={points}
        color={color}
        lineWidth={1}
        transparent
        opacity={opacity}
      />
    </group>
  );
}

function Satellite({ orbitRadius, orbitSpeed, orbitTilt, id, type = 'COMMS' }: {
  orbitRadius: number;
  orbitSpeed: number;
  orbitTilt: number;
  id: number;
  type?: 'COMMS' | 'WEATHER' | 'RECON';
}) {
  const groupRef = useRef<THREE.Group>(null);
  const sensorRef = useRef<THREE.Mesh>(null);
  const angleRef = useRef(id * (Math.PI * 2 / 3));
  const [hovered, setHovered] = useState(false);
  const { activeSatelliteId, setActiveSatelliteId, setSatelliteActive } = usePrismStore();

  const isActive = activeSatelliteId === id;

  useFrame((_, delta) => {
    if (!groupRef.current) return;
    angleRef.current += delta * orbitSpeed;
    const x = Math.cos(angleRef.current) * orbitRadius;
    const z = Math.sin(angleRef.current) * orbitRadius;
    groupRef.current.position.set(x, 0, z);
    groupRef.current.lookAt(0, 0, 0);
    groupRef.current.rotateY(Math.PI);

    // Scale animation based on hover/active state
    const targetScale = hovered || isActive ? 1.5 : 1.0;
    groupRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), delta * 5);
  });

  const coneHeight = orbitRadius - 1.01;
  const coneGeom = useMemo(() => {
    const radius = isActive ? 0.25 : 0.06;
    const geom = new THREE.ConeGeometry(radius, coneHeight, 16, 1, true);
    // Shift so tip is at origin (satellite), base extends downwards
    geom.translate(0, -coneHeight / 2, 0);
    // Rotate so it extends along -Z axis (which points to Earth after lookAt)
    geom.rotateX(Math.PI / 2);
    return geom;
  }, [coneHeight, isActive]);

  const baseColor = type === 'WEATHER' ? 0x00ff88 : type === 'RECON' ? 0xff3366 : 0x00f5ff;

  const coneMat = useMemo(() => new THREE.MeshBasicMaterial({
    color: new THREE.Color(isActive ? 0xffffff : baseColor),
    transparent: true,
    opacity: isActive ? 0.15 : 0.06,
    side: THREE.DoubleSide,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  }), [isActive, baseColor]);

  const coneEdgeMat = useMemo(() => new THREE.MeshBasicMaterial({
    color: new THREE.Color(isActive ? 0xffffff : baseColor),
    transparent: true,
    opacity: isActive ? 0.6 : 0.2,
    wireframe: true,
    blending: THREE.AdditiveBlending,
  }), [isActive, baseColor]);

  return (
    <group rotation={[orbitTilt, 0, 0]}>
      <group 
        ref={groupRef} 
        onClick={(e) => {
          e.stopPropagation();
          setActiveSatelliteId(id);
          setSatelliteActive(true);
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
          document.body.style.cursor = 'pointer';
        }}
        onPointerOut={() => {
          setHovered(false);
          document.body.style.cursor = 'default';
        }}
       >
        {/* Satellite body */}
        <mesh>
          <boxGeometry args={[0.015, 0.015, 0.04]} />
          <meshBasicMaterial color={isActive ? 0xffffff : 0x00f5ff} />
        </mesh>
        {/* Solar panels */}
        <mesh position={[0.03, 0, 0]}>
          <boxGeometry args={[0.04, 0.001, 0.02]} />
          <meshBasicMaterial color={0x1a4488} />
        </mesh>
        <mesh position={[-0.03, 0, 0]}>
          <boxGeometry args={[0.04, 0.001, 0.02]} />
          <meshBasicMaterial color={0x1a4488} />
        </mesh>
      </group>
    </group>
  );
}

function ConnectionArc({ start, end, color }: {
  start: THREE.Vector3;
  end: THREE.Vector3;
  color: string;
}) {
  const lineRef = useRef<any>(null);

  const points = useMemo(() => {
    const pts = [];
    const segments = 32;
    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      const interpolated = new THREE.Vector3().lerpVectors(start, end, t);
      const elevation = Math.sin(Math.PI * t) * 0.3;
      const normalized = interpolated.clone().normalize().multiplyScalar(1.05 + elevation);
      pts.push(normalized);
    }
    return pts;
  }, [start, end]);

  useFrame((_, delta) => {
    if (lineRef.current?.material) {
      // Animate dash offset for a flowing signal effect
      lineRef.current.material.dashOffset -= delta * 0.5;
    }
  });

  return (
    <Line
      ref={lineRef}
      points={points}
      color={color}
      lineWidth={0.8}
      transparent
      opacity={0.6}
      dashed={true}
      dashScale={2}
      dashSize={1}
      gapSize={2}
    />
  );
}

// Grid overlay on Earth
function GridOverlay() {
  const gridLines = useMemo(() => {
    const lines = [];
    const radius = 1.01;

    // Latitude lines (every 30 degrees)
    for (let lat = -60; lat <= 60; lat += 30) {
      const latRad = (lat * Math.PI) / 180;
      const pts = [];
      const r = Math.cos(latRad) * radius;
      const y = Math.sin(latRad) * radius;
      for (let i = 0; i <= 64; i++) {
        const angle = (i / 64) * Math.PI * 2;
        pts.push(new THREE.Vector3(Math.cos(angle) * r, y, Math.sin(angle) * r));
      }
      lines.push({ points: pts, key: `lat-${lat}` });
    }

    // Longitude lines (every 45 degrees)
    for (let lng = 0; lng < 360; lng += 45) {
      const lngRad = (lng * Math.PI) / 180;
      const pts = [];
      for (let i = 0; i <= 64; i++) {
        const latRad = ((i / 64) * 180 - 90) * (Math.PI / 180);
        pts.push(new THREE.Vector3(
          Math.cos(latRad) * Math.cos(lngRad) * radius,
          Math.sin(latRad) * radius,
          Math.cos(latRad) * Math.sin(lngRad) * radius
        ));
      }
      lines.push({ points: pts, key: `lng-${lng}` });
    }

    return lines;
  }, []);

  return (
    <group>
      {gridLines.map(({ points, key }) => (
        <Line
          key={key}
          points={points}
          color="#00f5ff"
          lineWidth={0.3}
          transparent
          opacity={0.08}
        />
      ))}
    </group>
  );
}

// Connection arcs
const ARC_CONFIGS = [
  { startLat: 39, startLng: 35, endLat: 51.5, endLng: -0.1, color: '#00f5ff' },  // Turkey → London
  { startLat: 40.7, startLng: -74, endLat: 48.8, endLng: 2.3, color: '#00ffcc' }, // NYC → Paris
  { startLat: 35.7, startLng: 139.7, endLat: 1.3, endLng: 103.8, color: '#00c8e0' }, // Tokyo → Singapore
  { startLat: 55.7, startLng: 37.6, endLat: 39.9, endLng: 116.4, color: '#00f5ff' }, // Moscow → Beijing
  { startLat: -33.9, startLng: 18.4, endLat: -23.5, endLng: -46.6, color: '#00ffcc' }, // Cape Town → São Paulo
];

function latLngToVec(lat: number, lng: number): THREE.Vector3 {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -Math.sin(phi) * Math.cos(theta),
    Math.cos(phi),
    Math.sin(phi) * Math.sin(theta)
  );
}

export default function OrbitalSystem() {
  const arcPoints = useMemo(() =>
    ARC_CONFIGS.map(c => ({
      start: latLngToVec(c.startLat, c.startLng),
      end: latLngToVec(c.endLat, c.endLng),
      color: c.color,
    })), []);

  return (
    <group>
      {/* Satellites ONLY - Rings, grids, and arcs removed for clean look */}
      <Satellite orbitRadius={1.4} orbitSpeed={0.8} orbitTilt={0.4} id={0} type="COMMS" />
      <Satellite orbitRadius={1.6} orbitSpeed={-0.5} orbitTilt={-0.6} id={1} type="WEATHER" />
      <Satellite orbitRadius={1.85} orbitSpeed={0.35} orbitTilt={0.2} id={2} type="RECON" />
    </group>
  );
}
