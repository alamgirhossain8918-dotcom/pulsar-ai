import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import { cn } from "../lib/utils";

interface HealthIndicatorProps {
  status: "HEALTHY" | "DEGRADED" | "DOWN" | string;
  latency?: number;
  label?: string;
}

export function HealthIndicator({ status, latency, label }: HealthIndicatorProps) {
  const isHealthy = status === "HEALTHY";
  const isDegraded = status === "DEGRADED";

  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-card border border-border">
      <div className="flex items-center gap-2.5">
        {isHealthy ? (
          <CheckCircle2 className="w-4 h-4 text-bullish" />
        ) : isDegraded ? (
          <AlertTriangle className="w-4 h-4 text-yellow-500" />
        ) : (
          <XCircle className="w-4 h-4 text-bearish" />
        )}
        <span className="text-xs font-medium text-white">{label || "Service"}</span>
      </div>

      <div className="flex items-center gap-3">
        {latency !== undefined && (
          <span className="text-[11px] font-mono text-neutral">{latency.toFixed(1)} ms</span>
        )}
        <span
          className={cn(
            "text-[10px] uppercase font-bold px-2 py-0.5 rounded",
            isHealthy
              ? "bg-bullish/10 text-bullish"
              : isDegraded
              ? "bg-yellow-500/10 text-yellow-500"
              : "bg-bearish/10 text-bearish"
          )}
        >
          {status}
        </span>
      </div>
    </div>
  );
}
