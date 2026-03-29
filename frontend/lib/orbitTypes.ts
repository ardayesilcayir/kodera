/** Mirrors backend `request_models.OrbitDesignRequest` / FastAPI contract. */

export type MissionType = 'EMERGENCY_COMMS' | 'EARTH_OBSERVATION' | 'BALANCED' | 'BROADCAST';

export type ContinuousCoverageStrategy = 'strict_24_7' | 'high_availability';

export type SensorModelType = 'communications' | 'optical' | 'radar' | 'generic';

export type PrimaryOptimizationGoal =
  | 'MINIMIZE_TOTAL_COST'
  | 'MINIMIZE_SATELLITE_COUNT'
  | 'MAXIMIZE_COVERAGE_FRACTION'
  | 'MINIMIZE_MAX_GAP_DURATION'
  | 'MINIMIZE_MEAN_RESPONSE_LATENCY';

export type SecondaryOptimizationGoal =
  | 'MINIMIZE_LAUNCH_MASS'
  | 'MINIMIZE_PROPULSION_BUDGET'
  | 'MAXIMIZE_REDUNDANCY'
  | 'MINIMIZE_GROUND_SEGMENT_COMPLEXITY';

export type OrbitFamily = 'LEO' | 'SSO' | 'MEO' | 'GEO' | 'HEO' | 'ELLIPTICAL';

export interface GeoJSONPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

export type RegionInput =
  | { mode: 'point_radius'; lat: number; lon: number; radius_km: number }
  | { mode: 'polygon'; polygon: GeoJSONPolygon };

export interface MissionSpec {
  type: MissionType;
  continuous_coverage_required: boolean;
  analysis_horizon_hours: number;
  validation_horizon_days: number;
  continuous_coverage_strategy?: ContinuousCoverageStrategy;
  target_min_point_coverage?: number;
  target_max_worst_cell_gap_seconds?: number | null;
}

export interface SensorModelSpec {
  type: SensorModelType;
  min_elevation_deg: number;
  sensor_half_angle_deg: number;
  max_off_nadir_deg: number;
  min_access_duration_s: number;
}

export interface OptimizationSpec {
  primary_goal: PrimaryOptimizationGoal;
  secondary_goals: SecondaryOptimizationGoal[];
  allowed_orbit_families: OrbitFamily[];
  max_satellites: number;
  max_planes: number;
}

export interface OrbitDesignRequestBody {
  region: RegionInput;
  mission: MissionSpec;
  sensor_model: SensorModelSpec;
  optimization: OptimizationSpec;
}

/** Backend `coverage_service.CoverageMetrics` after JSON round-trip. */
export interface CoverageMetricsJson {
  min_point_coverage: number;
  mean_point_coverage: number;
  overall_coverage_ratio: number;
  max_gap_seconds: number;
  worst_cell_gap_seconds: number;
  revisit_mean_seconds: number;
  revisit_median_seconds: number;
  continuous_24_7_feasible: boolean;
}

export interface RankedRecommendationJson {
  orbit_family: OrbitFamily | string;
  altitude_km: number;
  inclination_deg: number;
  total_satellites_T: number;
  planes_P: number;
  phase_F: number;
  metrics: CoverageMetricsJson;
  cost_score: number;
  complexity_score: number;
}

/** Backend design engine output (decrypted). */
export interface DesignResultJson {
  continuous_coverage_required: boolean;
  recommended: RankedRecommendationJson | null;
  evaluations: unknown[];
  explanations: string[];
  ai_engineering_summary?: string;
}

export interface DesignGenerateSuccess {
  status: 'success';
  feature: string;
  encrypted_data: string;
  raw_preview?: Record<string, unknown>;
}

export interface DesignGenerateError {
  status: 'error';
  message: string;
}

export interface DecryptSuccess {
  status: 'success';
  decrypted_data: DesignResultJson;
}

export interface DecryptError {
  status: 'error';
  message: string;
}

/** One successful design + decrypt round-trip for UI state. */
export interface ScanSession {
  request: OrbitDesignRequestBody;
  design: DesignResultJson;
}
