from typing import Optional
from pydantic import BaseModel


class DealingRange(BaseModel):
    range_high: float
    range_low: float
    equilibrium: float  # 0.50
    ote_62: float       # 0.618
    ote_705: float      # 0.705 (Sweet spot)
    ote_79: float       # 0.786
    current_price: float
    zone: str           # "DISCOUNT", "PREMIUM", "EQUILIBRIUM", "OTE_BUY", "OTE_SELL"


class PremiumDiscountEngine:
    """Calculates ICT Dealing Ranges, Equilibrium, Premium/Discount, and OTE zones"""

    @staticmethod
    def calculate_dealing_range(
        current_price: float,
        range_high: float,
        range_low: float
    ) -> DealingRange:
        if range_high <= range_low:
            range_high = range_low + 1.0

        diff = range_high - range_low
        eq = range_low + (diff * 0.5)

        # Fibonacci retracement levels from low to high:
        # For Longs: Retracement downwards from High to Low:
        # 62% retracement = High - (diff * 0.618)
        # 70.5% = High - (diff * 0.705)
        # 79% = High - (diff * 0.786)
        ote_62 = round(range_high - (diff * 0.618), 2)
        ote_705 = round(range_high - (diff * 0.705), 2)
        ote_79 = round(range_high - (diff * 0.786), 2)

        # Determine zone
        if ote_79 <= current_price <= ote_62:
            zone = "OTE_BUY"
        elif current_price < eq:
            zone = "DISCOUNT"
        elif (range_low + diff * 0.618) <= current_price <= (range_low + diff * 0.786):
            zone = "OTE_SELL"
        elif current_price > eq:
            zone = "PREMIUM"
        else:
            zone = "EQUILIBRIUM"

        return DealingRange(
            range_high=round(range_high, 2),
            range_low=round(range_low, 2),
            equilibrium=round(eq, 2),
            ote_62=ote_62,
            ote_705=ote_705,
            ote_79=ote_79,
            current_price=round(current_price, 2),
            zone=zone
        )
