"use client";

import { useEffect, useRef } from "react";
import { createChart, ColorType, IChartApi, ISeriesApi } from "lightweight-charts";
import { Candle, ChartMarker } from "../types";

interface LightweightChartProps {
  candles: Candle[];
  markers?: ChartMarker[];
  height?: number;
}

export function LightweightChart({ candles, markers = [], height = 450 }: LightweightChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { type: ColorType.Solid, color: "#121721" },
        textColor: "#9CA3AF",
      },
      grid: {
        vertLines: { color: "#181F2C" },
        horzLines: { color: "#181F2C" },
      },
      crosshair: {
        vertLine: { color: "#3B82F6", width: 1, style: 2 },
        horzLine: { color: "#3B82F6", width: 1, style: 2 },
      },
      rightPriceScale: {
        borderColor: "#232D3F",
      },
      timeScale: {
        borderColor: "#232D3F",
        timeVisible: true,
        secondsVisible: false,
      },
    });

    const candleSeries = chart.addCandlestickSeries({
      upColor: "#10B981",
      downColor: "#EF4444",
      borderVisible: false,
      wickUpColor: "#10B981",
      wickDownColor: "#EF4444",
    });

    chartRef.current = chart;
    seriesRef.current = candleSeries;

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [height]);

  // Update candle data and markers
  useEffect(() => {
    if (!seriesRef.current || !candles.length) return;

    // Filter and sort strictly by time
    const sorted = [...candles]
      .filter((c) => c && c.time)
      .sort((a, b) => (a.time as number) - (b.time as number));

    seriesRef.current.setData(sorted as any);

    if (markers.length) {
      const sortedMarkers = [...markers]
        .filter((m) => m && m.time)
        .sort((a, b) => a.time - b.time);
      seriesRef.current.setMarkers(sortedMarkers as any);
    }
  }, [candles, markers]);

  return (
    <div className="w-full relative rounded-lg overflow-hidden border border-border">
      <div ref={chartContainerRef} className="w-full" />
    </div>
  );
}
