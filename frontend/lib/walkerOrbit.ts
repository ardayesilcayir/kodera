/**
 * Walker Delta slot layout + circular orbit positions, aligned with backend
 * `walker_service.walker_delta_slots` and standard ECI→Three.js (Y-up) mapping.
 */

import * as THREE from 'three';

export const R_EARTH_KM = 6371.0;
export const MU_EARTH_KM3_S2 = 398600.4418;

/** Earth sidereal rotation: 2π / 86164.1s ≈ 7.2921e-5 rad/s */
export const EARTH_ROTATION_RAD_S = (2 * Math.PI) / 86164.1;

/**
 * Shared visual time multiplier so Earth and satellites stay in sync.
 * 600x → Earth rotates once every ~144s, LEO sat orbits every ~10s.
 */
export const VISUAL_TIME_SCALE = 600;

export interface WalkerSlot {
  index: number;
  planeIndex: number;
  raanRad: number;
  meanAnomalyRad: number;
}

/** Same indexing as backend `walker_service.walker_delta_slots`. */
export function walkerDeltaSlots(totalSatellitesT: number, planesP: number, phaseF: number): WalkerSlot[] {
  if (totalSatellitesT < 1 || planesP < 1) throw new Error('T and P must be positive.');
  if (totalSatellitesT % planesP !== 0) {
    throw new Error('Walker Delta requires T divisible by P.');
  }
  const s = totalSatellitesT / planesP;
  if (phaseF < 0 || phaseF >= planesP) {
    throw new Error('Walker phase F must satisfy 0 <= F < P.');
  }
  const out: WalkerSlot[] = [];
  for (let idx = 0; idx < totalSatellitesT; idx++) {
    const p = Math.floor(idx / s);
    const k = idx % s;
    const raan = (2.0 * Math.PI / planesP) * p;
    let m0 = (2.0 * Math.PI / s) * k + (2.0 * Math.PI / totalSatellitesT) * phaseF * p;
    m0 = Math.atan2(Math.sin(m0), Math.cos(m0));
    out.push({ index: idx, planeIndex: p, raanRad: raan, meanAnomalyRad: m0 });
  }
  return out;
}

/**
 * ECI equatorial (Z = north pole), circular orbit. Then map to Three.js Y-up:
 * (x, y, z)_three = (x_eci, z_eci, -y_eci)
 */
export function circularOrbitPositionThreeJs(
  radiusScene: number,
  inclinationRad: number,
  raanRad: number,
  meanAnomalyRad: number
): THREE.Vector3 {
  const cosI = Math.cos(inclinationRad);
  const sinI = Math.sin(inclinationRad);
  const cO = Math.cos(raanRad);
  const sO = Math.sin(raanRad);
  const cM = Math.cos(meanAnomalyRad);
  const sM = Math.sin(meanAnomalyRad);

  const xEci = radiusScene * (cO * cM - sO * sM * cosI);
  const yEci = radiusScene * (sO * cM + cO * sM * cosI);
  const zEci = radiusScene * (sM * sinI);

  return new THREE.Vector3(xEci, zEci, -yEci);
}

/** Earth mesh radius = 1 unit ⇒ r_scene = 1 + h/R_earth. */
export function altitudeKmToSceneRadius(altitudeKm: number): number {
  return 1 + altitudeKm / R_EARTH_KM;
}

/** Mean motion [rad/s] for circular orbit, r in km. */
export function meanMotionRadPerSec(altitudeKm: number): number {
  const rKm = R_EARTH_KM + altitudeKm;
  return Math.sqrt(MU_EARTH_KM3_S2 / (rKm * rKm * rKm));
}

/** Orbit ring polyline: one full revolution in the orbital plane (constant Ω, varying anomaly). */
export function orbitRingPointsThreeJs(
  radiusScene: number,
  inclinationRad: number,
  raanRad: number,
  segments = 128
): THREE.Vector3[] {
  const pts: THREE.Vector3[] = [];
  for (let i = 0; i <= segments; i++) {
    const M = (i / segments) * Math.PI * 2;
    pts.push(circularOrbitPositionThreeJs(radiusScene, inclinationRad, raanRad, M));
  }
  return pts;
}
