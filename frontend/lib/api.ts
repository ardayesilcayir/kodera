const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface OrbitDesignRequest {
  region: {
    mode: 'point_radius' | 'polygon';
    lat?: number;
    lon?: number;
    radius_km?: number;
    polygon?: any;
  };
  mission: {
    type: string;
    continuous_coverage_required: boolean;
    analysis_horizon_hours: number;
    validation_horizon_days: number;
    continuous_coverage_strategy?: string;
    target_min_point_coverage?: number;
    target_max_worst_cell_gap_seconds?: number | null;
  };
  sensor_model: {
    type: string;
    min_elevation_deg: number;
    sensor_half_angle_deg: number;
    max_off_nadir_deg: number;
    min_access_duration_s: number;
  };
  optimization: {
    primary_goal: string;
    secondary_goals: string[];
    allowed_orbit_families: string[];
    max_satellites: number;
    max_planes: number;
  };
}

export const api = {
  async generateConstellation(data: OrbitDesignRequest) {
    const response = await fetch(`${API_BASE_URL}/api/v1/design/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Constellation generation failed');
    return response.json();
  },

  async repositionSatellite(data: any) {
    const response = await fetch(`${API_BASE_URL}/api/v1/design/reposition`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Reposition failed');
    return response.json();
  },

  async decryptToken(encrypted_token: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/design/decrypt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ encrypted_token }),
    });
    if (!response.ok) throw new Error('Decryption failed');
    return response.json();
  },
  
  async getMe(token: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) throw new Error('Failed to fetch profile');
    return response.json();
  }
};
