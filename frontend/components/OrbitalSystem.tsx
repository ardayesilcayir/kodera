'use client';

import { useRef, useMemo, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Line } from '@react-three/drei';
import { usePrismStore } from '@/lib/store';
import { FLEET_SATELLITES, type FleetSatellite } from '@/lib/satellites';
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
        <Line key={`ring-${pi}`} points={pts} color="#00f5ff" lineWidth={0.6} transparent opacity={0.22} />
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

function FleetSatelliteMesh({ sat, highlighted }: { sat: FleetSatellite; highlighted: boolean }) {
  const groupRef = useRef<THREE.Group>(null);
  const Mref = useRef(THREE.MathUtils.degToRad(sat.phase_deg));
  const simulationSpeedMultiplier = usePrismStore((s) => s.simulationSpeedMultiplier);
  const selectedCountry = usePrismStore((s) => s.selectedCountry);
  const isEarthDragging = usePrismStore((s) => s.isEarthDragging);
  const selectFleetSat = usePrismStore((s) => s.selectFleetSat);
  const selectedFleetSatId = usePrismStore((s) => s.selectedFleetSatId);
  const maneuverResult = usePrismStore((s) => s.maneuverResult);
  const [hovered, setHovered] = useState(false);

  const hasNewOrbit = highlighted && maneuverResult?.best_plan?.target_orbit;
  const targetOrbit = maneuverResult?.best_plan?.target_orbit;

  const baseR = useMemo(() => altitudeKmToSceneRadius(sat.altitude_km), [sat.altitude_km]);
  const baseInc = useMemo(() => THREE.MathUtils.degToRad(sat.inclination_deg), [sat.inclination_deg]);
  const baseRaan = useMemo(() => THREE.MathUtils.degToRad(sat.raan_deg), [sat.raan_deg]);
  const baseMM = useMemo(() => meanMotionRadPerSec(sat.altitude_km), [sat.altitude_km]);

  const newR = hasNewOrbit ? altitudeKmToSceneRadius(targetOrbit!.altitude_km) : baseR;
  const newInc = hasNewOrbit ? THREE.MathUtils.degToRad(targetOrbit!.inclination_deg) : baseInc;
  const newRaan = hasNewOrbit ? THREE.MathUtils.degToRad(targetOrbit!.raan_deg) : baseRaan;
  const newMM = hasNewOrbit ? meanMotionRadPerSec(targetOrbit!.altitude_km) : baseMM;

  const lerpR = useRef(baseR);
  const lerpInc = useRef(baseInc);
  const lerpRaan = useRef(baseRaan);
  const lerpMM = useRef(baseMM);

  useFrame((_, delta) => {
    if (!groupRef.current) return;

    const lerpSpeed = delta * 0.8;
    lerpR.current += (newR - lerpR.current) * lerpSpeed;
    lerpInc.current += (newInc - lerpInc.current) * lerpSpeed;
    lerpRaan.current += (newRaan - lerpRaan.current) * lerpSpeed;
    lerpMM.current += (newMM - lerpMM.current) * lerpSpeed;

    const paused = !!selectedCountry || isEarthDragging;
    if (!paused) {
      Mref.current += lerpMM.current * delta * VISUAL_TIME_SCALE * simulationSpeedMultiplier;
      if (Mref.current > Math.PI * 2) Mref.current -= Math.PI * 2;
    }

    const pos = circularOrbitPositionThreeJs(lerpR.current, lerpInc.current, lerpRaan.current, Mref.current);
    groupRef.current.position.copy(pos);
    groupRef.current.lookAt(0, 0, 0);
    groupRef.current.rotateY(Math.PI);

    const targetScale = highlighted || hovered ? 1.8 : 1.0;
    groupRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), delta * 5);
  });

  const bodyColor = highlighted ? 0xffffff : sat.color;

  return (
    <group ref={groupRef}>
      <group
        onClick={(e) => {
          e.stopPropagation();
          selectFleetSat(selectedFleetSatId === sat.id ? null : sat.id);
        }}
        onPointerOver={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer'; }}
        onPointerOut={() => { setHovered(false); document.body.style.cursor = 'default'; }}
      >
        <mesh>
          <boxGeometry args={[0.014, 0.014, 0.036]} />
          <meshBasicMaterial color={bodyColor} />
        </mesh>
        <mesh position={[0.028, 0, 0]}>
          <boxGeometry args={[0.036, 0.001, 0.018]} />
          <meshBasicMaterial color={0x1a4488} />
        </mesh>
        <mesh position={[-0.028, 0, 0]}>
          <boxGeometry args={[0.036, 0.001, 0.018]} />
          <meshBasicMaterial color={0x1a4488} />
        </mesh>
        {highlighted && (
          <mesh>
            <sphereGeometry args={[0.05, 16, 16]} />
            <meshBasicMaterial color={sat.color} transparent opacity={0.15} />
          </mesh>
        )}
      </group>
    </group>
  );
}

function FleetConstellation() {
  const selectedFleetSatId = usePrismStore((s) => s.selectedFleetSatId);

  const rings = useMemo(() => {
    return FLEET_SATELLITES.map((sat) => {
      const rScene = altitudeKmToSceneRadius(sat.altitude_km);
      const incRad = THREE.MathUtils.degToRad(sat.inclination_deg);
      const raanRad = THREE.MathUtils.degToRad(sat.raan_deg);
      const pts = orbitRingPointsThreeJs(rScene, incRad, raanRad, 96);
      const hex = `#${sat.color.toString(16).padStart(6, '0')}`;
      return { id: sat.id, pts, hex };
    });
  }, []);

  return (
    <group>
      {rings.map((r) => (
        <Line
          key={`fleet-ring-${r.id}`}
          points={r.pts}
          color={r.id === selectedFleetSatId ? r.hex : r.hex}
          lineWidth={r.id === selectedFleetSatId ? 1.0 : 0.5}
          transparent
          opacity={r.id === selectedFleetSatId ? 0.35 : 0.12}
        />
      ))}
      {FLEET_SATELLITES.map((sat) => (
        <FleetSatelliteMesh key={sat.id} sat={sat} highlighted={sat.id === selectedFleetSatId} />
      ))}
    </group>
  );
}

function ManeuverTargetRing() {
  const maneuverResult = usePrismStore((s) => s.maneuverResult);
  if (!maneuverResult?.best_plan) return null;

  const targetOrbit = maneuverResult.best_plan.target_orbit;
  const rScene = altitudeKmToSceneRadius(targetOrbit.altitude_km);
  const incRad = THREE.MathUtils.degToRad(targetOrbit.inclination_deg);
  const raanRad = THREE.MathUtils.degToRad(targetOrbit.raan_deg);
  const pts = orbitRingPointsThreeJs(rScene, incRad, raanRad, 96);

  return <Line points={pts} color="#ffcc00" lineWidth={1.5} transparent opacity={0.45} dashed dashSize={0.02} gapSize={0.02} />;
}

export default function OrbitalSystem() {
  const scanResult = usePrismStore((s) => s.scanResult);
  const hasSolverGeometry = scanResult?.design.recommended != null;

  return (
    <group>
      <FleetConstellation />
      {hasSolverGeometry && <ConstellationFromScan />}
      <ManeuverTargetRing />
    </group>
  );
}
