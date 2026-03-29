import { create } from 'zustand';

export interface CountryData {
  name: string;
  lat: number;
  lng: number;
  signalStrength: number;
  activeSatellites: number;
  region: string;
}

export type MissionType = 'BALANCED' | 'EMERGENCY_COMMS' | 'EARTH_OBSERVATION' | 'BROADCAST';

interface PrismState {
  // Earth interaction
  isEarthHovered: boolean;
  isEarthDragging: boolean;
  earthScale: number;
  selectedCountry: CountryData | null;
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
  scanResult: any | null;
  scanError: string | null;

  // Satellite
  satelliteActive: boolean;
  activeSatelliteId: number;

  // Actions
  setEarthHovered: (hovered: boolean) => void;
  setEarthDragging: (dragging: boolean) => void;
  setEarthScale: (scale: number) => void;
  setShowClouds: (show: boolean) => void;
  setSelectedCountry: (country: CountryData | null) => void;
  setCameraZoomed: (zoomed: boolean) => void;
  setAiGenesisActive: (active: boolean) => void;
  setShowOptimizationResults: (show: boolean) => void;
  setSatelliteActive: (active: boolean) => void;
  setActiveSatelliteId: (id: number) => void;
  setMissionMode: (mode: MissionType) => void;
  runScan: () => Promise<void>;
  resetScan: () => void;
}

export const usePrismStore = create<PrismState>((set) => ({
  isEarthHovered: false,
  isEarthDragging: false,
  earthScale: 0.7,
  selectedCountry: null,
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

  setEarthHovered: (hovered) => set({ isEarthHovered: hovered }),
  setEarthDragging: (dragging) => set({ isEarthDragging: dragging }),
  setEarthScale: (scale) => set({ earthScale: scale }),
  setSelectedCountry: (country) => set({ selectedCountry: country }),
  setShowClouds: (show) => set({ showClouds: show }),
  setCameraZoomed: (zoomed) => set({ cameraZoomed: zoomed }),
  setAiGenesisActive: (active) => set({ aiGenesisActive: active }),
  setShowOptimizationResults: (show) => set({ showOptimizationResults: show }),
  setSatelliteActive: (active) => set({ satelliteActive: active }),
  setActiveSatelliteId: (id) => set({ activeSatelliteId: id }),
  setMissionMode: (mode) => set({ missionMode: mode }),
  
  runScan: async () => {
    const state = usePrismStore.getState();
    if (!state.selectedCountry) return;

    set({ isScanning: true, scanError: null });
    
    try {
      const { api } = await import('@/lib/api');
      
      const payload = {
        region: {
          mode: 'point_radius' as const,
          lat: state.selectedCountry.lat,
          lon: state.selectedCountry.lng,
          radius_km: 1000,
        },
        mission: {
          type: state.missionMode,
          continuous_coverage_required: true,
          analysis_horizon_hours: 24,
          validation_horizon_days: 7,
          target_min_point_coverage: 0.995,
        },
        sensor_model: {
          type: state.missionMode === 'EARTH_OBSERVATION' ? 'optical' : 'communications',
          min_elevation_deg: 10,
          sensor_half_angle_deg: 30,
          max_off_nadir_deg: 45,
          min_access_duration_s: 60,
        },
        optimization: {
          primary_goal: state.missionMode === 'EMERGENCY_COMMS' ? 'MINIMIZE_MAX_GAP_DURATION' : 'MINIMIZE_SATELLITE_COUNT',
          secondary_goals: ['MINIMIZE_PROPULSION_BUDGET'],
          allowed_orbit_families: ['LEO'],
          max_satellites: 48,
          max_planes: 6,
        }
      };

      const result = await api.generateConstellation(payload);
      set({ scanResult: result, isScanning: false });
    } catch (e: any) {
      set({ scanError: e.message || 'Scan failed', isScanning: false });
    }
  },

  resetScan: () => set({ scanResult: null, scanError: null, isScanning: false }),
}));
