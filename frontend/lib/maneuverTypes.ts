export interface ManeuverRequestBody {
  satellite_id: string;
  satellite_name: string;
  current_altitude_km: number;
  current_inclination_deg: number;
  current_raan_deg: number;
  current_phase_deg: number;
  satellite_mission_type: string;
  mission_type: string;
  target_lat: number;
  target_lon: number;
  target_radius_km: number;
  optimization_mode: string;
  max_transfer_time_hours: number;
}

export interface OrbitalStateJson {
  altitude_km: number;
  inclination_deg: number;
  raan_deg: number;
  phase_deg: number;
  eccentricity: number;
}

export interface TransferSummaryJson {
  delta_v_altitude_km_s: number;
  delta_v_inclination_km_s: number;
  delta_v_total_km_s: number;
  transfer_time_seconds: number;
  transfer_time_hours: number;
  transfer_cost_score: number;
  altitude_change_km: number;
  inclination_change_deg: number;
  raan_change_deg: number;
  raan_cost_score: number;
}

export interface ManeuverCoverageJson {
  target_region_coverage: number;
  coverage_gain: number;
  continuity_score: number;
  revisit_score: number;
}

export interface RiskAnalysisJson {
  zone_risk: number;
  proximity_risk: number;
  satellite_risk: number;
  transfer_risk: number;
  total_risk_score: number;
  risk_factors: string[];
}

export interface SystemImpactJson {
  redundancy_score: number;
  overlap_penalty: number;
  gap_reduction: number;
  strategic_fit_score: number;
  constellation_balance: number;
}

export interface RepositionPlanJson {
  rank: number;
  target_orbit: OrbitalStateJson;
  transfer_summary: TransferSummaryJson;
  coverage_metrics: ManeuverCoverageJson;
  system_impact: SystemImpactJson;
  risk_analysis: RiskAnalysisJson;
  explanation: string;
  confidence_score: number;
  feasibility_score: number;
  limitations: string[];
  final_score: number;
  score_breakdown: Record<string, number>;
  operational_status: string;
  violated_constraints: string[];
}

export interface ManeuverResultData {
  best_plan: RepositionPlanJson;
  alternative_plans: RepositionPlanJson[];
  total_candidates_evaluated: number;
  optimization_mode: string;
  best_feasible_plan: RepositionPlanJson | null;
  model_mode: string;
  summary: string;
  ai_engineering_summary?: string;
}

export interface ManeuverApiResponse {
  status: 'success' | 'error';
  feature?: string;
  data?: ManeuverResultData;
  message?: string;
}
