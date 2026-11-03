import { cn } from "../lib/utils";

interface RegimeBadgeProps {
  regime: string;
  className?: string;
}

export function RegimeBadge({ regime, className }: RegimeBadgeProps) {
  let color = "bg-neutral/10 text-neutral border-neutral/20";

  if (regime.includes("Strong Bullish")) {
    color = "bg-bullish/20 text-bullish border-bullish/40 font-bold";
  } else if (regime.includes("Bullish")) {
    color = "bg-bullish/10 text-bullish border-bullish/30";
  } else if (regime.includes("Strong Bearish")) {
    color = "bg-bearish/20 text-bearish border-bearish/40 font-bold";
  } else if (regime.includes("Bearish")) {
    color = "bg-bearish/10 text-bearish border-bearish/30";
  } else if (regime.includes("Ranging")) {
    color = "bg-yellow-500/10 text-yellow-400 border-yellow-500/30";
  } else if (regime.includes("Volatility")) {
    color = "bg-purple-500/10 text-purple-400 border-purple-500/30";
  }

  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs border font-medium",
        color,
        className
      )}
    >
      {regime}
    </span>
  );
}
