# Orbital design engine (local backend)

Deterministic regional-coverage constellation design: strict Pydantic request validation, Walker candidate enumeration, footprint pruning, visibility simulation, and ranking.

## Input contract (project rule)

**Public HTTP API:** one JSON object with four top-level keys only — `region`, `mission`, `sensor_model`, `optimization` (same schema as `OrbitDesignRequest` in `request_models.py`). The client does **not** send Walker grids, simulation step, or footprint parameters; those are built internally in `api/default_pipeline.py` from the mission type, `continuous_coverage_required`, and `optimization.max_satellites` / `max_planes` (single source of truth for limits).

**Library / tests:** you may still construct `CandidateGenerationInput` and `DesignerParams` explicitly and call `designer_service.run_design(...)` (see `tests/test_design_pipeline.py`).

**Allowed internal constants** (engine): Earth physical parameters, angle/unit conversions, and numerical tolerances that do not change mission meaning.

## Map / frontend: what to send when the user picks a location

| User action | You must supply in `region` | Notes |
|-------------|------------------------------|--------|
| Click a **single point** (marker) | `mode: "point_radius"`, **`lat`**, **`lon`**, **`radius_km`** | The engine does not accept a zero-area point; **choose a radius** (e.g. 25–150 km) for the area of interest. Coordinates must be **WGS84** in decimal degrees (same as most web maps). |
| Draw a **polygon** | `mode: "polygon"`, **`polygon`** (GeoJSON `Polygon`, closed ring, lon/lat) | First and last vertex must match; holes optional. |

Everything else in `OrbitDesignRequest` comes from **mission presets**, **sensor / link budget form fields**, and **optimization limits** — not from the map alone:

| Block | Typical source on the UI |
|-------|---------------------------|
| `mission` | Scenario template (e.g. emergency comms vs EO), **continuous** yes/no, **strategy** (`strict_24_7` vs `high_availability`), analysis horizon, validation horizon |
| `sensor_model` | Min elevation mask, **payload cone** (`sensor_half_angle_deg`), optional steering cap (`max_off_nadir_deg`), **minimum dwell** (`min_access_duration_s`) — all are now applied in the link simulation |
| `optimization` | User caps: `max_satellites`, `max_planes`, allowed orbit families, primary/secondary goals |

**Not** taken from the map: Walker `T|P|F`, altitude grids, simulation time step, Earth rotation model (defaults in `default_designer_params`).

**Footprint prefilter** (before simulation) uses **min elevation** and a solid-angle bound only; the time-stepping simulation applies the **full link model** (elevation + nadir cone + minimum dwell). Rare edge cases may still differ from a full mission analysis tool (drag, SGP4, terrain, weather).

## Requirements

- Python 3.9+
- Dependencies: see `requirements.txt` (includes FastAPI and Uvicorn for the HTTP API).

## Setup

```bash
cd optimization_location
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the API

From the `optimization_location` directory (so `app` and `api` resolve correctly):

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) — request body schema is **`OrbitDesignRequest`**.

## Design endpoint

**POST** `/api/v1/design/orbit`

**Request body:** `OrbitDesignRequest` — `region` (polygon or point+radius), `mission`, `sensor_model`, `optimization`.

**Responses**

- **200** — structured design result (`recommended_architecture`, `top_candidates`, `feasibility_summary`, `coverage_metrics`, `explanation`).
- **422** — validation failed or inconsistent inputs.

**Feasibility semantics**

- If `mission.continuous_coverage_required` is **false** (typical EO / revisit analysis), any simulated candidate can be ranked; `coverage_metrics.continuous_24_7_feasible` may still be **false** (partial coverage over the horizon).
- If **continuous coverage is required**:
  - **`continuous_coverage_strategy`: `strict_24_7`** (default): hard requirement that every ground grid point has a satellite above min elevation at **every** time step over `analysis_horizon_hours`. A recommendation is emitted only when `coverage_metrics.mission_objective_met` is **true** (equivalent to strict `continuous_24_7_feasible` here).
  - **`high_availability`**: engineering-style targets — `target_min_point_coverage` (worst cell’s time fraction with visibility) and optional `target_max_worst_cell_gap_seconds`. Use this for “near 24/7” constellations without demanding a perfect all-`true` visibility matrix.
- `feasibility_summary.recommended_feasible` follows `mission_objective_met` on the chosen architecture.

**Propagation (simulation fidelity)**

- Default designer parameters use **J2 mean-element secular rates** on RAAN, argument of perigee, and mean anomaly, plus **Vallado-style GMST** for ECI→ECEF (see `DesignerParams` / `propagator_service`). Two-body-only and simplified Earth spin remain selectable for regression or fast sweeps.

**Optimization ranking**

- Among feasible candidates, ordering follows `optimization.primary_goal` with lexicographic tie-breakers (`optimization_ranking`): e.g. `MINIMIZE_SATELLITE_COUNT` minimizes `T` first, then worst-cell gap, then cost/complexity proxies.

**Logging** (INFO on `kodera.design.optimizer`): after Walker enumeration — total candidates and counts by orbit family, altitude (km), inclination (deg), and Walker `T|P|F` strings; after evaluation — footprint-pruned count vs simulated count. A WARNING is logged if fewer than five candidates are enumerated (intentionally tiny search space vs missing grid expansion).

### Example with curl

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/design/orbit \
  -H "Content-Type: application/json" \
  -d @samples/api_design_request.json | jq .

# Earth observation (SSO-only families), Marmara polygon:
curl -s -X POST http://127.0.0.1:8000/api/v1/design/orbit \
  -H "Content-Type: application/json" \
  -d @samples/api_design_request_realistic_eo.json | jq .

# Emergency comms + continuous coverage, LEO-only search:
curl -s -X POST http://127.0.0.1:8000/api/v1/design/orbit \
  -H "Content-Type: application/json" \
  -d @samples/api_design_request_continuous_comms.json | jq .
```

Sample files:

- `samples/api_design_request.json` — **canonical** public contract (point+radius, EMERGENCY_COMMS, four orbit families); one `curl` works as-is.
- `samples/api_design_request_realistic_eo.json` — EO mission, Marmara polygon, SSO-only `allowed_orbit_families`.
- `samples/api_design_request_continuous_comms.json` — small polygon, continuous coverage, LEO-only.
- `samples/api_design_response.json` — example 200 response shape (may drift; regenerate if needed).

## Tests

```bash
pytest tests/ -q
```

API tests use `httpx` + `TestClient` (included via FastAPI test utilities).

## Library usage (no HTTP)

Call `designer_service.run_design(request, candidate_input, designer_params)` with a validated `OrbitDesignRequest` plus explicit `CandidateGenerationInput` and `DesignerParams`; see `tests/test_design_pipeline.py`. For HTTP, defaults are applied in `api/default_pipeline.py`.
