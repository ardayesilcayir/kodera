export interface FleetSatellite {
  id: string;
  name: string;
  altitude_km: number;
  inclination_deg: number;
  raan_deg: number;
  phase_deg: number;
  mission_type: 'communication' | 'observation' | 'emergency' | 'balanced';
  color: number;
  description: string;
}

export const FLEET_SATELLITES: FleetSatellite[] = [
  {
    id: 'sat-leo-comm-01',
    name: 'ORION-1',
    altitude_km: 550,
    inclination_deg: 53.0,
    raan_deg: 0,
    phase_deg: 0,
    mission_type: 'communication',
    color: 0x00f5ff,
    description: 'LEO Comm Relay',
  },
  {
    id: 'sat-leo-comm-02',
    name: 'ORION-2',
    altitude_km: 550,
    inclination_deg: 53.0,
    raan_deg: 120,
    phase_deg: 180,
    mission_type: 'communication',
    color: 0x00f5ff,
    description: 'LEO Comm Relay',
  },
  {
    id: 'sat-sso-obs-01',
    name: 'SENTINEL-1',
    altitude_km: 780,
    inclination_deg: 97.4,
    raan_deg: 108,
    phase_deg: 90,
    mission_type: 'observation',
    color: 0x00ffcc,
    description: 'SSO Observation',
  },
  {
    id: 'sat-meo-nav-01',
    name: 'ATLAS-1',
    altitude_km: 2000,
    inclination_deg: 55.0,
    raan_deg: 60,
    phase_deg: 45,
    mission_type: 'balanced',
    color: 0x44aaff,
    description: 'MEO Navigation',
  },
  {
    id: 'sat-leo-emer-01',
    name: 'PHOENIX-1',
    altitude_km: 420,
    inclination_deg: 51.6,
    raan_deg: 200,
    phase_deg: 120,
    mission_type: 'emergency',
    color: 0xff6644,
    description: 'LEO Emergency',
  },
];
