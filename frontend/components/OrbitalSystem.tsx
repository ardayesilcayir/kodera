'use client';

import { useRef, useMemo, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Line } from '@react-three/drei';
import { usePrismStore } from '@/lib/store';
import {
  walkerDeltaSlots,
  circularOrbitPositionThreeJs,
  altitudeKmToSceneRadius,
  meanMotionRadPerSec,
  orbitRingPointsThreeJs,
  VISUAL_TIME_SCALE,
} from '@/lib/walkerOrbit';

function WalkerSatelliteMesh({
  index,
  rScene,
  incRad,
  raanRad,
  M0,
  meanMotion,
  color,
}: {
  index: number;
  rScene: number;
  incRad: number;
  raanRad: number;
  M0: number;
  meanMotion: number;
  color: number;
}) {
  const groupRef = useRef<THREE.Group>(null);
  const Mref = useRef(M0);
  const [hovered, setHovered] = useState(false);
  const activeSatelliteId = usePrismStore((s) => s.activeSatelliteId);
  const setActiveSatelliteId = usePrismStore((s) => s.setActiveSatelliteId);
  const setSatelliteActive = usePrismStore((s) => s.setSatelliteActive);
  const simulationSpeedMultiplier = usePrismStore((s) => s.simulationSpeedMultiplier);
  const selectedCountry = usePrismStore((s) => s.selectedCountry);
  const isEarthDragging = usePrismStore((s) => s.isEarthDragging);
  const isActive = activeSatelliteId === index;

  useFrame((_, delta) => {
    if (!groupRef.current) return;

    const paused = !!selectedCountry || isEarthDragging;
    if (!paused) {
      Mref.current += meanMotion * delta * VISUAL_TIME_SCALE * simulationSpeedMultiplier;
      if (Mref.current > Math.PI * 2) Mref.current -= Math.PI * 2;
      if (Mref.current < 0) Mref.current += Math.PI * 2;
    }

    const pos = circularOrbitPositionThreeJs(rScene, incRad, raanRad, Mref.current);
    groupRef.current.position.copy(pos);
    groupRef.current.lookAt(0, 0, 0);
    groupRef.current.rotateY(Math.PI);
    const targetScale = hovered || isActive ? 1.5 : 1.0;
    groupRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), delta * 5);
  });

  return (
    <group ref={groupRef}>
      <group
        onClick={(e) => {
          e.stopPropagation();
          setActiveSatelliteId(index);
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
        <mesh>
          <boxGeometry args={[0.014, 0.014, 0.036]} />
          <meshBasicMaterial color={isActive ? 0xffffff : color} />
        </mesh>
        <mesh position={[0.028, 0, 0]}>
          <boxGeometry args={[0.036, 0.001, 0.018]} />
          <meshBasicMaterial color={0x1a4488} />
        </mesh>
        <mesh position={[-0.028, 0, 0]}>
          <boxGeometry args={[0.036, 0.001, 0.018]} />
          <meshBasicMaterial color={0x1a4488} />
        </mesh>
      </group>
    </group>
  );
}

function ConstellationFromScan() {
  const scanResult = usePrismStore((s) => s.scanResult);
  const rec = scanResult?.design.recommended;

  const spec = useMemo(() => {
    if (!rec) return null;
    try {
      const T = rec.total_satellites_T;
      const P = rec.planes_P;
      const F = rec.phase_F;
      const slots = walkerDeltaSlots(T, P, F);
      const rScene = altitudeKmToSceneRadius(rec.altitude_km);
      const incRad = THREE.MathUtils.degToRad(rec.inclination_deg);
      const mm = meanMotionRadPerSec(rec.altitude_km);
      const planeRings = Array.from({ length: P }, (_, p) => {
        const raan = (2 * Math.PI) / P * p;
        return orbitRingPointsThreeJs(rScene, incRad, raan, 96);
      });
      const colors = [0x00f5ff, 0x00ffcc, 0x44aaff, 0x88ccff];
      return { slots, rScene, incRad, mm, planeRings, colors };
    } catch {
      return null;
    }
  }, [rec]);

  if (!spec) return null;

  const { slots, rScene, incRad, mm, planeRings, colors } = spec;

  return (
    <group>
      {planeRings.map((pts, pi) => (
        <Line
          key={`ring-${pi}`}
          points={pts}
          color="#00f5ff"
          lineWidth={0.6}
          transparent
          opacity={0.22}
        />
      ))}
      {slots.map((slot, i) => (
        <WalkerSatelliteMesh
          key={slot.index}
          index={i}
          rScene={rScene}
          incRad={incRad}
          raanRad={slot.raanRad}
          M0={slot.meanAnomalyRad}
          meanMotion={mm}
          color={colors[i % colors.length]}
        />
      ))}
    </group>
  );
}

/**
 * Pre-optimized realistic constellation: 3 LEO satellites across 2 planes.
 * Plane 1 (inc 53°, alt 550km): 2 sats — LEO comm relay
 * Plane 2 (inc 97.4°, alt 780km): 1 sat — SSO observation
 */
function DefaultConstellation() {
  const simulationSpeedMultiplier = usePrismStore((s) => s.simulationSpeedMultiplier);

  const spec = useMemo(() => {
    const plane1Alt = 550;
    const plane1Inc = THREE.MathUtils.degToRad(53);
    const plane1Raan = 0;
    const plane1R = altitudeKmToSceneRadius(plane1Alt);
    const plane1MM = meanMotionRadPerSec(plane1Alt);
    const plane1Ring = orbitRingPointsThreeJs(plane1R, plane1Inc, plane1Raan, 96);

    const plane2Alt = 780;
    const plane2Inc = THREE.MathUtils.degToRad(97.4);
    const plane2Raan = Math.PI * 0.6;
    const plane2R = altitudeKmToSceneRadius(plane2Alt);
    const plane2MM = meanMotionRadPerSec(plane2Alt);
    const plane2Ring = orbitRingPointsThreeJs(plane2R, plane2Inc, plane2Raan, 96);

    return {
      sats: [
        { rScene: plane1R, incRad: plane1Inc, raanRad: plane1Raan, M0: 0, mm: plane1MM, color: 0x00f5ff },
        { rScene: plane1R, incRad: plane1Inc, raanRad: plane1Raan, M0: Math.PI, mm: plane1MM, color: 0x00f5ff },
        { rScene: plane2R, incRad: plane2Inc, raanRad: plane2Raan, M0: Math.PI * 0.5, mm: plane2MM, color: 0x00ffcc },
      ],
      rings: [
        { pts: plane1Ring, color: '#00f5ff' },
        { pts: plane2Ring, color: '#00ffcc' },
      ],
    };
  }, []);

  return (
    <group>
      {spec.rings.map((ring, i) => (
        <Line key={`default-ring-${i}`} points={ring.pts} color={ring.color} lineWidth={0.5} transparent opacity={0.15} />
      ))}
      {spec.sats.map((s, i) => (
        <WalkerSatelliteMesh
          key={`default-sat-${i}`}
          index={1000 + i}
          rScene={s.rScene}
          incRad={s.incRad}
          raanRad={s.raanRad}
          M0={s.M0}
          meanMotion={s.mm}
          color={s.color}
        />
      ))}
    </group>
  );
}

export default function OrbitalSystem() {
  const scanResult = usePrismStore((s) => s.scanResult);
  const hasSolverGeometry = scanResult?.design.recommended != null;

  return (
    <group>
      {hasSolverGeometry ? <ConstellationFromScan /> : <DefaultConstellation />}
    </group>
  );
}
