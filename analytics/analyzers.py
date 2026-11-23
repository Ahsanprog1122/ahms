"""Financial and Risk Analyzers for AHMS.

Pure Python OOP math using Decimal.
"""

from decimal import Decimal
from typing import Dict, List, Tuple
from .portfolio import Portfolio


class FinancialAnalyzer:
    """Calculates financial returns: Gain, ROI, Annualized Return, CAGR, and FIFO gains."""

    @staticmethod
    def calculate_gain(current_value: Decimal, cost_basis: Decimal) -> Decimal:
        return Decimal(str(current_value)) - Decimal(str(cost_basis))

    @staticmethod
    def calculate_roi(current_value: Decimal, cost_basis: Decimal) -> Decimal:
        c_val = Decimal(str(current_value))
        c_basis = Decimal(str(cost_basis))
        if c_basis == Decimal("0"):
            return Decimal("0")
        return ((c_val - c_basis) / c_basis) * Decimal("100")

    @staticmethod
    def calculate_cagr(start_value: Decimal, end_value: Decimal, years: Decimal, round_digits: int = 1) -> Decimal:
        s_val = float(start_value)
        e_val = float(end_value)
        y = float(years)
        if s_val <= 0 or y <= 0:
            return Decimal("0")
        cagr_float = ((e_val / s_val) ** (1.0 / y) - 1.0) * 100.0
        return Decimal(str(round(cagr_float, round_digits)))

    @staticmethod
    def calculate_fifo_realized_gain(
        buy_lots: List[Tuple[Decimal, Decimal]],
        sell_quantity: Decimal,
        sell_price_per_unit: Decimal,
    ) -> Tuple[Decimal, List[Tuple[Decimal, Decimal]]]:
        remaining_to_sell = Decimal(str(sell_quantity))
        sell_price = Decimal(str(sell_price_per_unit))
        realized_gain = Decimal("0")
        new_lots: List[Tuple[Decimal, Decimal]] = []

        for qty, price in buy_lots:
            lot_qty = Decimal(str(qty))
            lot_price = Decimal(str(price))
            if remaining_to_sell <= Decimal("0"):
                new_lots.append((lot_qty, lot_price))
            elif lot_qty <= remaining_to_sell:
                realized_gain += lot_qty * (sell_price - lot_price)
                remaining_to_sell -= lot_qty
            else:
                realized_gain += remaining_to_sell * (sell_price - lot_price)
                remaining_lot_qty = lot_qty - remaining_to_sell
                new_lots.append((remaining_lot_qty, lot_price))
                remaining_to_sell = Decimal("0")

        return realized_gain, new_lots


class RiskAnalyzer:
    """Evaluates portfolio risk: category concentration, HHI, and liquid share."""

    @staticmethod
    def calculate_hhi(category_shares: Dict[str, Decimal]) -> Decimal:
        if not category_shares:
            return Decimal("0")
        return sum((share ** 2 for share in category_shares.values()), Decimal("0"))

    @staticmethod
    def calculate_largest_holding_share(portfolio: Portfolio) -> Decimal:
        total = portfolio.total_value()
        if total == Decimal("0") or not portfolio.assets:
            return Decimal("0")
        max_val = max(a.current_value() for a in portfolio.assets)
        return max_val / total
