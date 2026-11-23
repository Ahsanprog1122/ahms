"""Health score evaluation logic for AHMS."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from .base import Asset
from .portfolio import Portfolio
from .analyzers import RiskAnalyzer


@dataclass
class ScoreSettings:
    """Configurable scoring parameters and indicator weights."""

    weight_profitability: Decimal = Decimal("0.25")
    weight_diversification: Decimal = Decimal("0.20")
    weight_liquidity: Decimal = Decimal("0.15")
    weight_risk: Decimal = Decimal("0.15")
    weight_growth: Decimal = Decimal("0.15")
    weight_income: Decimal = Decimal("0.10")

    profitability_min: Decimal = Decimal("0.0")
    profitability_max: Decimal = Decimal("12.0")

    diversification_norm: Decimal = Decimal("0.8")
    liquidity_target: Decimal = Decimal("0.50")

    risk_low_concentration: Decimal = Decimal("0.20")
    risk_high_concentration: Decimal = Decimal("0.60")

    growth_min: Decimal = Decimal("0.0")
    growth_max: Decimal = Decimal("10.0")

    income_min: Decimal = Decimal("0.0")
    income_max: Decimal = Decimal("4.0")


@dataclass
class HealthScoreResult:
    """Full breakdown of the portfolio health score evaluation."""

    profitability_score: Decimal
    diversification_score: Decimal
    liquidity_score: Decimal
    risk_score: Decimal
    growth_score: Decimal
    income_score: Decimal
    total_score: Decimal
    band: str
    hhi: Decimal
    largest_holding_share: Decimal
    liquid_share: Decimal


class AssetHealthStatus:
    """Per-asset health classifier."""

    WEAK = "Weak"
    WATCH = "Watch"
    HEALTHY = "Healthy"

    @classmethod
    def evaluate(
        cls,
        asset: Asset,
        portfolio_total_value: Decimal,
        as_of: Optional[date] = None,
        twelve_month_growth_rate: Optional[Decimal] = None,
    ) -> str:
        ref_date = as_of or date.today()
        days_held = (ref_date - asset.purchase_date).days

        cost = asset.total_cost_basis()
        c_val = asset.current_value()
        peak_val = asset.peak_valuation_value()

        is_held_12m = days_held >= 365
        has_negative_return = c_val < cost
        is_down_20_from_peak = peak_val > Decimal("0") and ((peak_val - c_val) / peak_val) > Decimal("0.20")

        if (is_held_12m and has_negative_return) or is_down_20_from_peak:
            return cls.WEAK

        latest_val = asset.latest_valuation()
        valuation_outdated = False
        if latest_val:
            if (ref_date - latest_val.valuation_date).days > 90:
                valuation_outdated = True
        elif days_held > 90:
            valuation_outdated = True

        is_over_concentrated = (
            portfolio_total_value > Decimal("0") and (c_val / portfolio_total_value) > Decimal("0.25")
        )

        has_no_income = asset.annual_income(ref_date) <= Decimal("0")
        has_no_growth = (twelve_month_growth_rate is not None and twelve_month_growth_rate <= Decimal("0"))

        if valuation_outdated or is_over_concentrated or (has_no_income and has_no_growth):
            return cls.WATCH

        return cls.HEALTHY


class AssetHealthEvaluator:
    """Evaluates portfolio health and produces 0-100 score."""

    def __init__(self, settings: Optional[ScoreSettings] = None):
        self.settings = settings or ScoreSettings()

    def evaluate_portfolio(
        self,
        portfolio: Portfolio,
        annualized_return_pct: Decimal,
        growth_12m_pct: Decimal,
        income_yield_pct: Decimal,
    ) -> HealthScoreResult:
        # 1. Profitability
        p_ret = Decimal(str(annualized_return_pct))
        if p_ret <= self.settings.profitability_min:
            profitability_score = Decimal("0.0")
        elif p_ret >= self.settings.profitability_max:
            profitability_score = Decimal("100.0")
        else:
            profitability_score = (
                (p_ret - self.settings.profitability_min)
                / (self.settings.profitability_max - self.settings.profitability_min)
            ) * Decimal("100.0")

        # 2. Diversification
        cat_shares = portfolio.category_shares()
        hhi = RiskAnalyzer.calculate_hhi(cat_shares)
        div_score_raw = ((Decimal("1.0") - hhi) / self.settings.diversification_norm) * Decimal("100.0")
        diversification_score = max(Decimal("0.0"), min(Decimal("100.0"), div_score_raw))

        # 3. Liquidity
        liq_share = portfolio.liquid_share()
        liq_score_raw = (liq_share / self.settings.liquidity_target) * Decimal("100.0")
        liquidity_score = max(Decimal("0.0"), min(Decimal("100.0"), liq_score_raw))

        # 4. Risk exposure
        largest_share = RiskAnalyzer.calculate_largest_holding_share(portfolio)
        r_low = self.settings.risk_low_concentration
        r_high = self.settings.risk_high_concentration
        if largest_share <= r_low:
            risk_score = Decimal("100.0")
        elif largest_share >= r_high:
            risk_score = Decimal("0.0")
        else:
            risk_score = ((r_high - largest_share) / (r_high - r_low)) * Decimal("100.0")

        # 5. Growth
        g_pct = Decimal(str(growth_12m_pct))
        if g_pct <= self.settings.growth_min:
            growth_score = Decimal("0.0")
        elif g_pct >= self.settings.growth_max:
            growth_score = Decimal("100.0")
        else:
            growth_score = (
                (g_pct - self.settings.growth_min)
                / (self.settings.growth_max - self.settings.growth_min)
            ) * Decimal("100.0")

        # 6. Income
        inc_pct = Decimal(str(income_yield_pct))
        if inc_pct <= self.settings.income_min:
            income_score = Decimal("0.0")
        elif inc_pct >= self.settings.income_max:
            income_score = Decimal("100.0")
        else:
            income_score = (
                (inc_pct - self.settings.income_min)
                / (self.settings.income_max - self.settings.income_min)
            ) * Decimal("100.0")

        # Weighted Total Score
        total_score = (
            (profitability_score * self.settings.weight_profitability)
            + (diversification_score * self.settings.weight_diversification)
            + (liquidity_score * self.settings.weight_liquidity)
            + (risk_score * self.settings.weight_risk)
            + (growth_score * self.settings.weight_growth)
            + (income_score * self.settings.weight_income)
        )

        if total_score >= Decimal("80.0"):
            band = "Healthy"
        elif total_score >= Decimal("60.0"):
            band = "Moderately Healthy"
        elif total_score >= Decimal("40.0"):
            band = "Needs Improvement"
        else:
            band = "Financially Weak"

        return HealthScoreResult(
            profitability_score=profitability_score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
            diversification_score=diversification_score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
            liquidity_score=liquidity_score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
            risk_score=risk_score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
            growth_score=growth_score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
            income_score=income_score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
            total_score=total_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            band=band,
            hhi=hhi.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
            largest_holding_share=largest_share.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
            liquid_share=liq_share.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
        )
