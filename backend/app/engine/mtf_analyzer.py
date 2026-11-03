from typing import Dict, List, Optional
import pandas as pd
from pydantic import BaseModel
from backend.app.indicators.technical import enrich_technical_indicators
from backend.app.market_structure.structure import MarketStructureAnalysis, MarketTrend, StructureBreak
from backend.app.liquidity.liquidity_engine import LiquidityEngine, LiquidityPool, LiquiditySweepEvent, SessionLevels
from backend.app.liquidity.fvg import FVGEngine, FairValueGap
from backend.app.liquidity.order_block import OrderBlockEngine, OrderBlock
from backend.app.liquidity.premium_discount import PremiumDiscountEngine, DealingRange
from backend.app.engine.regime import MarketRegimeDetector, MarketRegimeResult


class TimeframeAnalysis(BaseModel):
    timeframe: str
    trend: MarketTrend
    regime: MarketRegimeResult
    breaks: List[StructureBreak]
    recent_high: Optional[float]
    recent_low: Optional[float]
    fvgs: List[FairValueGap]
    order_blocks: List[OrderBlock]
    dealing_range: DealingRange
    session_levels: SessionLevels
    sweeps: List[LiquiditySweepEvent]


class MTFAnalysisResult(BaseModel):
    symbol: str
    htf_bias: MarketTrend
    macro_regime: MarketRegimeResult
    tf_analyses: Dict[str, TimeframeAnalysis]
    active_dealing_range: DealingRange
    provider: str
    is_demo: bool = False


class MultiTimeframeAnalyzer:
    """Analyzes market data across multiple timeframes (5m, 15m, 1h, 4h, 1d)"""

    @classmethod
    def analyze_single_timeframe(cls, df: pd.DataFrame, timeframe: str) -> TimeframeAnalysis:
        # 1. Enrich with indicators
        df_enriched = enrich_technical_indicators(df)

        # 2. Market Structure Analysis
        breaks, trend, r_high, r_low = MarketStructureAnalysis.evaluate_structure(df_enriched)

        # 3. Market Regime
        regime = MarketRegimeDetector.detect_regime(df_enriched, trend)

        # 4. Liquidity & Sweeps
        pools, sweeps = LiquidityEngine.detect_liquidity_sweeps(df_enriched)
        session_levels = LiquidityEngine.calculate_session_and_macro_levels(df_enriched)

        # 5. FVGs
        fvgs = FVGEngine.detect_fvgs(df_enriched)

        # 6. Order Blocks
        obs = OrderBlockEngine.detect_order_blocks(df_enriched, breaks)

        # 7. Dealing Range
        last_close = float(df_enriched['close'].iloc[-1])
        high_bound = r_high if r_high is not None else float(df_enriched['high'].max())
        low_bound = r_low if r_low is not None else float(df_enriched['low'].min())
        dealing_range = PremiumDiscountEngine.calculate_dealing_range(last_close, high_bound, low_bound)

        return TimeframeAnalysis(
            timeframe=timeframe,
            trend=trend,
            regime=regime,
            breaks=breaks[-5:] if breaks else [],  # Keep latest 5
            recent_high=r_high,
            recent_low=r_low,
            fvgs=fvgs[-8:] if fvgs else [],
            order_blocks=obs[-5:] if obs else [],
            dealing_range=dealing_range,
            session_levels=session_levels,
            sweeps=sweeps[-5:] if sweeps else []
        )

    @classmethod
    def analyze_symbol(
        cls,
        symbol: str,
        timeframe_dfs: Dict[str, pd.DataFrame],
        provider: str = "binance",
        is_demo: bool = False
    ) -> MTFAnalysisResult:
        tf_analyses: Dict[str, TimeframeAnalysis] = {}

        for tf, df in timeframe_dfs.items():
            if not df.empty and len(df) >= 15:
                tf_analyses[tf] = cls.analyze_single_timeframe(df, tf)

        # Higher Timeframe Bias from 4h or 1d or highest available
        htf_key = "4h" if "4h" in tf_analyses else ("1d" if "1d" in tf_analyses else ("1h" if "1h" in tf_analyses else "15m"))
        htf_analysis = tf_analyses.get(htf_key)

        htf_bias = htf_analysis.trend if htf_analysis else MarketTrend.NEUTRAL
        macro_regime = htf_analysis.regime if htf_analysis else MarketRegimeDetector.detect_regime(pd.DataFrame(), MarketTrend.NEUTRAL)
        active_dealing_range = htf_analysis.dealing_range if htf_analysis else PremiumDiscountEngine.calculate_dealing_range(100.0, 110.0, 90.0)

        return MTFAnalysisResult(
            symbol=symbol,
            htf_bias=htf_bias,
            macro_regime=macro_regime,
            tf_analyses=tf_analyses,
            active_dealing_range=active_dealing_range,
            provider=provider,
            is_demo=is_demo
        )
