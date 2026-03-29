'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePrismStore } from '@/lib/store';
import type { RepositionPlanJson } from '@/lib/maneuverTypes';

function Metric({ label, value, unit }: { label: string; value: string | number; unit?: string }) {
  return (
    <div className="flex justify-between items-center">
      <span className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.5)] uppercase">{label}</span>
      <span className="font-mono-tech text-[10px] text-[#00f5ff] tabular-nums">
        {value}{unit && <span className="text-[8px] text-[rgba(0,245,255,0.4)] ml-0.5">{unit}</span>}
      </span>
    </div>
  );
}

function ScoreBar({ label, value, max = 1 }: { label: string; value: number; max?: number }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  return (
    <div className="space-y-0.5">
      <div className="flex justify-between items-center">
        <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.5)] uppercase">{label}</span>
        <span className="font-mono-tech text-[9px] text-[#00f5ff] tabular-nums">{(value * 100).toFixed(1)}%</span>
      </div>
      <div className="w-full h-1 rounded-full overflow-hidden" style={{ background: 'rgba(0,245,255,0.1)' }}>
        <motion.div
          className="h-full rounded-full"
          style={{ background: 'linear-gradient(90deg, #00f5ff, #00ffcc)' }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}

function PlanCard({ plan, expanded, toggle }: { plan: RepositionPlanJson; expanded: boolean; toggle: () => void }) {
  const t = plan.transfer_summary;
  const c = plan.coverage_metrics;
  return (
    <motion.div
      className="rounded border p-2 cursor-pointer"
      style={{ background: 'rgba(0,10,20,0.5)', borderColor: expanded ? 'rgba(0,245,255,0.4)' : 'rgba(0,245,255,0.1)' }}
      onClick={toggle}
      layout
    >
      <div className="flex justify-between items-center">
        <span className="font-mono-tech text-[9px] text-[#00f5ff] font-bold">PLAN #{plan.rank}</span>
        <span className="font-mono-tech text-[9px] text-[#00ffcc] tabular-nums">{(plan.final_score * 100).toFixed(1)} pts</span>
      </div>
      <AnimatePresence>
        {expanded && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="mt-2 space-y-1.5 overflow-hidden">
            <Metric label="Alt" value={plan.target_orbit.altitude_km.toFixed(1)} unit="km" />
            <Metric label="Inc" value={plan.target_orbit.inclination_deg.toFixed(2)} unit="°" />
            <Metric label="Dv Total" value={t.delta_v_total_km_s.toFixed(4)} unit="km/s" />
            <Metric label="Transfer" value={t.transfer_time_hours.toFixed(1)} unit="h" />
            <ScoreBar label="Coverage" value={c.target_region_coverage} />
            <ScoreBar label="Confidence" value={plan.confidence_score} />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function ManeuverResultsPanel() {
  const isManeuverRunning = usePrismStore((s) => s.isManeuverRunning);
  const maneuverResult = usePrismStore((s) => s.maneuverResult);
  const maneuverError = usePrismStore((s) => s.maneuverError);
  const resetManeuver = usePrismStore((s) => s.resetManeuver);
  const selectFleetSat = usePrismStore((s) => s.selectFleetSat);

  const [progress, setProgress] = useState(0);
  const [expandedPlan, setExpandedPlan] = useState<number | null>(null);

  useEffect(() => {
    if (!isManeuverRunning) { setProgress(maneuverResult ? 100 : 0); return; }
    setProgress(0);
    const start = Date.now();
    const id = setInterval(() => {
      const elapsed = Date.now() - start;
      setProgress(Math.min(92, (1 - Math.exp(-elapsed / 25000)) * 100));
    }, 300);
    return () => clearInterval(id);
  }, [isManeuverRunning, maneuverResult]);

  const best = maneuverResult?.best_plan;
  const alts = maneuverResult?.alternative_plans ?? [];

  const handleDismiss = () => {
    resetManeuver();
  };

  const handleBack = () => {
    resetManeuver();
    selectFleetSat(null);
  };

  return (
    <motion.div
      className="glass-panel scanlines relative overflow-hidden select-none"
      style={{ width: '280px', padding: '32px 24px', maxHeight: '75vh', display: 'flex', flexDirection: 'column' }}
      initial={{ x: 60, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      {/* HUD corners */}
      <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-cyan-400 opacity-70" />
      <div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-cyan-400 opacity-70" />
      <div className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-cyan-400 opacity-70" />
      <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-cyan-400 opacity-70" />

      {/* Icon */}
      <div className="flex justify-center mb-4 relative z-10">
        <motion.div
          className="w-12 h-12 rounded-full flex items-center justify-center"
          style={{ border: '1px solid rgba(0,245,255,0.4)', background: 'rgba(0,245,255,0.05)', boxShadow: '0 0 20px rgba(0,245,255,0.2)' }}
          animate={isManeuverRunning ? { rotate: 360 } : {}}
          transition={isManeuverRunning ? { duration: 2, repeat: Infinity, ease: 'linear' } : {}}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00f5ff" strokeWidth="1.5">
            <circle cx="12" cy="12" r="3" />
            <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
            <path d="M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" />
          </svg>
        </motion.div>
      </div>

      {/* Title */}
      <div className="text-center mb-3 relative z-10">
        <span className="font-orbitron text-xs font-bold tracking-widest text-neon" style={{ fontSize: '11px', letterSpacing: '3px' }}>
          {isManeuverRunning ? 'COMPUTING' : 'REPOSITION'}
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full h-1 rounded-full overflow-hidden mb-4 relative z-10" style={{ background: 'rgba(0,245,255,0.08)' }}>
        <motion.div
          className="h-full rounded-full"
          style={{ background: 'linear-gradient(90deg, #00f5ff, #00ffcc)' }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
        />
      </div>

      {/* Divider */}
      <div className="w-full h-px mb-4 relative z-10" style={{ background: 'linear-gradient(90deg, transparent, rgba(0,245,255,0.4), transparent)' }} />

      {/* Scrollable results */}
      <div className="overflow-y-auto no-scrollbar flex-1 relative z-10 space-y-3">
        {isManeuverRunning && (
          <div className="text-center space-y-2">
            <span className="font-mono-tech text-[10px] text-[rgba(0,245,255,0.5)]">Analyzing orbital transfers...</span>
            <div className="flex justify-center gap-1">
              {[0, 1, 2].map((i) => (
                <motion.div key={i} className="w-1 h-1 rounded-full bg-[#00f5ff]" animate={{ opacity: [0.3, 1, 0.3] }} transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.3 }} />
              ))}
            </div>
          </div>
        )}

        {maneuverError && (
          <div className="text-center p-2 rounded border border-red-500/30 bg-red-500/5">
            <span className="font-mono-tech text-[10px] text-red-400">{maneuverError}</span>
          </div>
        )}

        {best && !isManeuverRunning && (
          <>
            {/* Best plan summary */}
            <div className="mb-1">
              <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] tracking-[3px] uppercase">BEST PLAN</span>
            </div>

            <div className="space-y-2 bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.15)] rounded p-2">
              <Metric label="Score" value={(best.final_score * 100).toFixed(1)} unit="pts" />
              <Metric label="Target Alt" value={best.target_orbit.altitude_km.toFixed(1)} unit="km" />
              <Metric label="Target Inc" value={best.target_orbit.inclination_deg.toFixed(2)} unit="°" />
              <Metric label="RAAN" value={best.target_orbit.raan_deg.toFixed(2)} unit="°" />
              <Metric label="Delta-V" value={best.transfer_summary.delta_v_total_km_s.toFixed(4)} unit="km/s" />
              <Metric label="Transfer Time" value={best.transfer_summary.transfer_time_hours.toFixed(1)} unit="h" />
              <Metric label="Status" value={best.operational_status} />
            </div>

            {/* Score bars */}
            <div className="space-y-2 mt-2">
              <ScoreBar label="Coverage" value={best.coverage_metrics.target_region_coverage} />
              <ScoreBar label="Coverage Gain" value={best.coverage_metrics.coverage_gain} />
              <ScoreBar label="Confidence" value={best.confidence_score} />
              <ScoreBar label="Feasibility" value={best.feasibility_score} />
            </div>

            {/* Risk */}
            {best.risk_analysis && (
              <div className="mt-2">
                <div className="mb-1">
                  <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] tracking-[3px] uppercase">RISK</span>
                </div>
                <div className="space-y-1 bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] rounded p-2">
                  <Metric label="Total Risk" value={(best.risk_analysis.total_risk_score * 100).toFixed(1)} unit="%" />
                  {best.risk_analysis.risk_factors?.slice(0, 3).map((f, i) => (
                    <span key={i} className="block font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)]">· {f}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Explanation */}
            {best.explanation && (
              <div className="mt-2">
                <div className="mb-1">
                  <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] tracking-[3px] uppercase">ANALYSIS</span>
                </div>
                <p className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.5)] leading-relaxed">{best.explanation}</p>
              </div>
            )}

            {/* Alternative plans */}
            {alts.length > 0 && (
              <div className="mt-3">
                <div className="mb-1">
                  <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] tracking-[3px] uppercase">ALTERNATIVES ({alts.length})</span>
                </div>
                <div className="space-y-2">
                  {alts.map((p) => (
                    <PlanCard
                      key={p.rank}
                      plan={p}
                      expanded={expandedPlan === p.rank}
                      toggle={() => setExpandedPlan(expandedPlan === p.rank ? null : p.rank)}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Summary */}
            {maneuverResult?.summary && (
              <div className="mt-2">
                <div className="mb-1">
                  <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] tracking-[3px] uppercase">SUMMARY</span>
                </div>
                <p className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.5)] leading-relaxed">{maneuverResult.summary}</p>
              </div>
            )}

            {/* AI Engineering Summary */}
            {maneuverResult?.ai_engineering_summary && (
              <div className="mt-3">
                <div className="mb-1 flex items-center gap-1.5">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#00f5ff" strokeWidth="2">
                    <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.8 2.8-2 3.5V11h3a3 3 0 0 1 3 3v1.5a2.5 2.5 0 0 1-5 0V14H9v1.5a2.5 2.5 0 0 1-5 0V14a3 3 0 0 1 3-3h3V9.5A4 4 0 0 1 12 2z" />
                  </svg>
                  <span className="font-mono-tech text-[8px] text-[rgba(0,245,255,0.4)] tracking-[3px] uppercase">AI ANALYSIS</span>
                </div>
                <div className="bg-[rgba(0,10,20,0.5)] border border-[rgba(0,245,255,0.1)] rounded p-2">
                  <p className="font-mono-tech text-[9px] text-[rgba(0,245,255,0.6)] leading-relaxed whitespace-pre-wrap">
                    {maneuverResult.ai_engineering_summary}
                  </p>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Footer buttons */}
      {(maneuverResult || maneuverError) && !isManeuverRunning && (
        <div className="flex gap-2 mt-4 relative z-10">
          <motion.button
            className="btn-neon flex-1 font-orbitron text-[9px]"
            style={{ background: 'rgba(0,245,255,0.05)' }}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={handleDismiss}
          >
            BACK
          </motion.button>
          <motion.button
            className="flex-1 font-orbitron text-[9px] rounded border border-[rgba(0,245,255,0.2)] text-[rgba(0,245,255,0.5)] hover:text-[#00f5ff] hover:border-[rgba(0,245,255,0.4)] py-1.5 transition-all"
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={handleBack}
          >
            DESELECT
          </motion.button>
        </div>
      )}

      {/* Accent line */}
      <motion.div
        className="absolute bottom-0 left-0 h-0.5"
        style={{ background: 'linear-gradient(90deg, transparent, #00f5ff, transparent)' }}
        animate={{ width: ['0%', '100%', '0%'] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      />
    </motion.div>
  );
}
