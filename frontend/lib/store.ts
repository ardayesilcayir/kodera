import { create } from 'zustand';

export interface CountryData {
  name: string;
  lat: number;
  lng: number;
  signalStrength: number;
  activeSatellites: number;
  region: string;
}

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
  assetFluxActive: boolean;

  // System metrics
  orbitalAssets: number;
  signalStrength: number;
  powerStatus: string;
  missionMode: 'BALANCED' | 'EMERGENCY_COMMS' | 'EARTH_OBSERVATION' | 'BROADCAST';

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
  setAssetFluxActive: (active: boolean) => void;
  setSatelliteActive: (active: boolean) => void;
  setActiveSatelliteId: (id: number) => void;
  setMissionMode: (mode: 'BALANCED' | 'EMERGENCY_COMMS' | 'EARTH_OBSERVATION' | 'BROADCAST') => void;
}

export const usePrismStore = create<PrismState>((set) => ({
  isEarthHovered: false,
  isEarthDragging: false,
  earthScale: 0.7,
  selectedCountry: null,
  cameraZoomed: false,
  showClouds: true,
  aiGenesisActive: false,
  assetFluxActive: false,
  orbitalAssets: 45,
  signalStrength: 98,
  powerStatus: 'STABLE',
  missionMode: 'BALANCED',
  satelliteActive: false,
  activeSatelliteId: 0,

  setEarthHovered: (hovered) => set({ isEarthHovered: hovered }),
  setEarthDragging: (dragging) => set({ isEarthDragging: dragging }),
  setEarthScale: (scale) => set({ earthScale: scale }),
  setSelectedCountry: (country) => set({ selectedCountry: country }),
  setShowClouds: (show) => set({ showClouds: show }),
  setCameraZoomed: (zoomed) => set({ cameraZoomed: zoomed }),
  setAiGenesisActive: (active) => set({ aiGenesisActive: active }),
  setAssetFluxActive: (active) => set({ assetFluxActive: active }),
  setSatelliteActive: (active) => set({ satelliteActive: active }),
  setActiveSatelliteId: (id) => set({ activeSatelliteId: id }),
  setMissionMode: (mode) => set({ missionMode: mode }),
}));
