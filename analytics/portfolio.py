"""Portfolio container and aggregations for AHMS.

Holds assets and aggregates portfolio-level metrics.
"""

from decimal import Decimal
from typing import Dict, List, Optional
from .base import Asset


class Portfolio:
    """Manages an aggregated collection of assets."""

    def __init__(self, name: str = "My Portfolio", portfolio_id: Optional[str] = None):
        self.name = name
        self.portfolio_id = portfolio_id
        self.assets: List[Asset] = []

    def add_asset(self, asset: Asset) -> None:
        self.assets.append(asset)

    def remove_asset(self, asset: Asset) -> None:
        if asset in self.assets:
            self.assets.remove(asset)

    def total_value(self) -> Decimal:
        return sum((a.current_value() for a in self.assets), Decimal("0"))

    def total_cost_basis(self) -> Decimal:
        return sum((a.total_cost_basis() for a in self.assets), Decimal("0"))

    def total_gain(self) -> Decimal:
        return self.total_value() - self.total_cost_basis()

    def category_values(self) -> Dict[str, Decimal]:
        breakdown: Dict[str, Decimal] = {}
        for asset in self.assets:
            cat = asset.category
            breakdown[cat] = breakdown.get(cat, Decimal("0")) + asset.current_value()
        return breakdown

    def category_shares(self) -> Dict[str, Decimal]:
        tot = self.total_value()
        if tot == Decimal("0"):
            return {}
        cat_vals = self.category_values()
        return {cat: val / tot for cat, val in cat_vals.items()}

    def liquid_value(self) -> Decimal:
        return sum((a.current_value() for a in self.assets if a.is_liquid), Decimal("0"))

    def liquid_share(self) -> Decimal:
        tot = self.total_value()
        if tot == Decimal("0"):
            return Decimal("0")
        return self.liquid_value() / tot

    def annual_income(self) -> Decimal:
        return sum((a.annual_income() for a in self.assets), Decimal("0"))

    def __repr__(self) -> str:
        return f"<Portfolio '{self.name}' assets={len(self.assets)} total_val={self.total_value()}>"
