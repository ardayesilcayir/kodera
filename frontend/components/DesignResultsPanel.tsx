'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { usePrismStore } from '@/lib/store';

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 border-b border-white/[0.06] py-1.5 last:border-0">
      <span className="font-mono-tech text-[8px] text-white/35 tracking-[2px] uppercase">{label}</span>
      <span className="font-orbitron text-[10px] text-cyan-300/90 text-right truncate max-w-[180px]">{value}</span>
    </div>
  );
}

export default function DesignResultsPanel() {
  const scanResult = usePrismStore((s) => s.scanResult);
  const rec = scanResult?.design.recommended;
  const req = scanResult?.request;
  const metrics = rec?.metrics;
  const expl = scanResult?.design.explanations ?? [];
  const ai = scanResult?.design.ai_engineering_summary;

  return (
    <AnimatePresence>
      {scanResult && (
        <motion.div
          className="fixed z-[45] pointer-events-none select-none"
          style={{
            left: '22%',
            top: '50%',
            transform: 'translateY(-50%)',
            width: 'min(320px, 28vw)',
          }}
          initial={{ opacity: 0, x: -24 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -24 }}
          transition={{ type: 'spring', damping: 28, stiffness: 220 }}
        >
          <div className="glass-panel border border-cyan-500/15 bg-black/50 backdrop-blur-xl rounded-xl px-5 py-4 shadow-[0_24px_80px_rgba(0,0,0,0.65)]">
            <div className="font-orbitron text-[9px] text-cyan-400/80 tracking-[6px] uppercase mb-3">
              GENERATE_SOLVER_OUTPUT
            </div>

            {rec ? (
              <>
                <Row label="WALKER_T_P_F" value={`${rec.total_satellites_T} | ${rec.planes_P} | ${rec.phase_F}`} />
                <Row label="ALT_KM" value={rec.altitude_km.toFixed(1)} />
                <Row label="INC_DEG" value={rec.inclination_deg.toFixed(2)} />
                <Row label="FAMILY" value={String(rec.orbit_family)} />
                <Row label="MIN_POINT_COV" value={(metrics?.min_point_coverage ?? 0).toFixed(5)} />
                <Row label="WORST_CELL_GAP_S" value={(metrics?.worst_cell_gap_seconds ?? 0).toFixed(1)} />
                <Row label="REVISIT_MED_S" value={(metrics?.revisit_median_seconds ?? 0).toFixed(1)} />
              </>
            ) : (
              <div className="font-mono-tech text-[9px] text-amber-400/80 py-2">
                No feasible ranked candidate (solver returned empty recommendation).
              </div>
            )}

            {req && (
              <div className="mt-3 pt-3 border-t border-white/10">
                <div className="font-mono-tech text-[7px] text-white/25 uppercase tracking-widest mb-2">REQUEST_LOCK</div>
                {req.region.mode === 'point_radius' && (
                  <>
                    <Row label="REGION_LAT" value={req.region.lat.toFixed(5)} />
                    <Row label="REGION_LON" value={req.region.lon.toFixed(5)} />
                    <Row label="RADIUS_KM" value={String(req.region.radius_km)} />
                  </>
                )}
                <Row label="MISSION" value={req.mission.type} />
                <Row label="HORIZON_H" value={String(req.mission.analysis_horizon_hours)} />
                <Row label="PRIMARY_GOAL" value={req.optimization.primary_goal} />
              </div>
            )}

            {expl.length > 0 && (
              <div className="mt-3 pt-3 border-t border-white/10">
                <div className="font-mono-tech text-[7px] text-white/25 uppercase tracking-widest mb-1">EXPLANATIONS</div>
                <ul className="space-y-1 font-mono-tech text-[8px] text-white/45 leading-relaxed list-disc pl-3">
                  {expl.slice(0, 3).map((line, i) => (
                    <li key={i}>{line}</li>
                  ))}
                </ul>
              </div>
            )}

            {ai && (
              <div className="mt-3 pt-3 border-t border-white/10">
                <div className="font-mono-tech text-[7px] text-white/25 uppercase tracking-widest mb-1">AI_SUMMARY</div>
                <p className="font-mono-tech text-[8px] text-cyan-200/50 leading-relaxed line-clamp-4">{ai}</p>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
