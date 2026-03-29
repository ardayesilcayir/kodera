import { create } from 'zustand';
import type { OrbitDesignRequestBody, ScanSession } from '@/lib/orbitTypes';

export interface CountryData {
  name: string;
  lat: number;
  lng: number;
  signalStrength: number;
  activeSatellites: number;
  region: string;
}

/** Raycast’ten gelen tam tıklama (generate `region` merkezi — yuvarlama yok). */
export interface SurfaceTarget {
  lat: number;
  lng: number;
}

export type MissionType = 'BALANCED' | 'EMERGENCY_COMMS' | 'EARTH_OBSERVATION' | 'BROADCAST';

/** Dünya dönüşü + uydu yörünge animasyonları ortak çarpan (1 = varsayılan). */
export const SIM_SPEED_MIN = 0.25;
export const SIM_SPEED_MAX = 50;
export const SIM_SPEED_STEP = 0.25;

interface PrismState {
  // Earth interaction
  isEarthHovered: boolean;
  isEarthDragging: boolean;
  earthScale: number;
  selectedCountry: CountryData | null;
  /** Son tıklanan yüzey noktası; `/design/generate` region merkezi buradan gider. */
  surfaceTarget: SurfaceTarget | null;
  cameraZoomed: boolean;
  showClouds: boolean;

  // Panel states
  aiGenesisActive: boolean;
  showOptimizationResults: boolean;

  // System metrics
  orbitalAssets: number;
  signalStrength: number;
  powerStatus: string;
  missionMode: MissionType;

  // Scan states
  isScanning: boolean;
  scanResult: ScanSession | null;
  scanError: string | null;

  // Satellite
  satelliteActive: boolean;
  activeSatelliteId: number;

  /** Simülasyon zaman ölçeği: Dünya dönüşü ve uydu mean-motion görsel hızı. */
  simulationSpeedMultiplier: number;

  // Actions
  setEarthHovered: (hovered: boolean) => void;
  setEarthDragging: (dragging: boolean) => void;
  setEarthScale: (scale: number) => void;
  setShowClouds: (show: boolean) => void;
  setSelectedCountry: (country: CountryData | null) => void;
  setSurfaceTarget: (target: SurfaceTarget | null) => void;
  setCameraZoomed: (zoomed: boolean) => void;
  setAiGenesisActive: (active: boolean) => void;
  setShowOptimizationResults: (show: boolean) => void;
  setSatelliteActive: (active: boolean) => void;
  setActiveSatelliteId: (id: number) => void;
  setMissionMode: (mode: MissionType) => void;
  runScan: () => Promise<void>;
  resetScan: () => void;
  adjustSimulationSpeed: (direction: -1 | 1) => void;
  setSimulationSpeedMultiplier: (value: number) => void;
}

export const usePrismStore = create<PrismState>((set) => ({
  isEarthHovered: false,
  isEarthDragging: false,
  earthScale: 0.7,
  selectedCountry: null,
  surfaceTarget: null,
  cameraZoomed: false,
  showClouds: true,
  aiGenesisActive: false,
  showOptimizationResults: false,
  orbitalAssets: 45,
  signalStrength: 98,
  powerStatus: 'STABLE',
  missionMode: 'BALANCED',
  isScanning: false,
  scanResult: null,
  scanError: null,
  satelliteActive: false,
  activeSatelliteId: 0,
  simulationSpeedMultiplier: 1,

  setEarthHovered: (hovered) => set({ isEarthHovered: hovered }),
  setEarthDragging: (dragging) => set({ isEarthDragging: dragging }),
  setEarthScale: (scale) => set({ earthScale: scale }),
  setSelectedCountry: (country) => set({ selectedCountry: country }),
  setSurfaceTarget: (target) => set({ surfaceTarget: target }),
  setShowClouds: (show) => set({ showClouds: show }),
  setCameraZoomed: (zoomed) => set({ cameraZoomed: zoomed }),
  setAiGenesisActive: (active) => set({ aiGenesisActive: active }),
  setShowOptimizationResults: (show) => set({ showOptimizationResults: show }),
  setSatelliteActive: (active) => set({ satelliteActive: active }),
  setActiveSatelliteId: (id) => set({ activeSatelliteId: id }),
  setMissionMode: (mode) => set({ missionMode: mode }),
  
  runScan: async () => {
    const state = usePrismStore.getState();
    const lat = state.surfaceTarget?.lat ?? state.selectedCountry?.lat;
    const lon = state.surfaceTarget?.lng ?? state.selectedCountry?.lng;
    if (lat == null || lon == null) return;

    set({ isScanning: true, scanError: null, scanResult: null });
    
    try {
      const { api } = await import('@/lib/api');
      
      const payload: OrbitDesignRequestBody = {
        region: {
          mode: 'point_radius',
          lat,
          lon,
          radius_km: 500,
        },
        mission: {
          type: state.missionMode,
          continuous_coverage_required: false,
          analysis_horizon_hours: 2,
          validation_horizon_days: 1,
          continuous_coverage_strategy: 'strict_24_7',
          target_min_point_coverage: 0.9,
          target_max_worst_cell_gap_seconds: null,
        },
        sensor_model: {
          type: state.missionMode === 'EARTH_OBSERVATION' ? 'optical' : 'communications',
          min_elevation_deg: 10,
          sensor_half_angle_deg: 30,
          max_off_nadir_deg: 45,
          min_access_duration_s: 60,
        },
        optimization: {
          primary_goal:
            state.missionMode === 'EMERGENCY_COMMS'
              ? 'MINIMIZE_MAX_GAP_DURATION'
              : 'MINIMIZE_SATELLITE_COUNT',
          secondary_goals: ['MINIMIZE_PROPULSION_BUDGET'],
          allowed_orbit_families: ['LEO'],
          max_satellites: 12,
          max_planes: 3,
        },
      };

      const result = await api.generateConstellation(payload);
      set({ scanResult: result, isScanning: false });
    } catch (e: any) {
      set({ scanError: e.message || 'Scan failed', isScanning: false });
    }
  },

  resetScan: () => set({ scanResult: null, scanError: null, isScanning: false }),

  adjustSimulationSpeed: (direction) =>
    set((s) => {
      const next = s.simulationSpeedMultiplier + direction * SIM_SPEED_STEP;
      return {
        simulationSpeedMultiplier: Math.min(SIM_SPEED_MAX, Math.max(SIM_SPEED_MIN, next)),
      };
    }),

  setSimulationSpeedMultiplier: (value) =>
    set((s) => {
      const n = Number(value);
      if (!Number.isFinite(n)) return {};
      return { simulationSpeedMultiplier: Math.min(SIM_SPEED_MAX, Math.max(SIM_SPEED_MIN, n)) };
    }),
}));
