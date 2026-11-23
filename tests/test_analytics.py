"""Must-pass test suite for AHMS Analytics Engine."""

from datetime import date
from decimal import Decimal
from analytics import (
    Stock,
    Land,
    Gold,
    CashAsset,
    Portfolio,
    FinancialAnalyzer,
    RiskAnalyzer,
    AssetHealthEvaluator,
    AssetHealthStatus,
    ScoreSettings,
)


def test_gain_and_roi():
    """Verify gain 125,000 - 100,000 = 25,000 and ROI 25%."""
    cost = Decimal("100000")
    current = Decimal("125000")

    gain = FinancialAnalyzer.calculate_gain(current, cost)
    roi = FinancialAnalyzer.calculate_roi(current, cost)

    assert gain == Decimal("25000")
    assert roi == Decimal("25.0")


def test_cagr():
    """Verify CAGR from 5,000,000 to 6,500,000 in 2 years = 14.0%."""
    start = Decimal("5000000")
    end = Decimal("6500000")
    years = Decimal("2")

    cagr = FinancialAnalyzer.calculate_cagr(start, end, years)
    assert cagr == Decimal("14.0")


def test_must_pass_reference_portfolio():
    """MUST-PASS TEST from system requirements:

    Portfolio PKR 10,000,000:
    - Plot A: 4,000,000 (real_estate)
    - Plot B: 2,000,000 (real_estate)
    - Stocks: 2,000,000 (stocks)
    - Gold: 1,200,000 (gold)
    - Cash: 800,000 (cash)

    Expected scores:
    - Profitability: 75.0
    - Diversification: 72.4 (HHI 0.4208)
    - Liquidity: 80.0
    - Risk: 50.0
    - Growth: 60.0
    - Income: 40.0
    - Total: 65.73
    - Band: Moderately Healthy
    """
    portfolio = Portfolio(name="Must Pass Reference Portfolio")

    plot_a = Land(
        name="Plot A",
        purchase_price=Decimal("4000000"),
        purchase_date=date(2023, 1, 1),
    )
    portfolio.add_asset(plot_a)

    plot_b = Land(
        name="Plot B",
        purchase_price=Decimal("2000000"),
        purchase_date=date(2023, 6, 1),
    )
    portfolio.add_asset(plot_b)

    stocks = Stock(
        name="PSX Stocks",
        purchase_price=Decimal("100"),
        purchase_date=date(2024, 1, 1),
        quantity=Decimal("20000"),
        latest_price=Decimal("100"),
    )
    portfolio.add_asset(stocks)

    gold = Gold(
        name="Gold Reserves",
        purchase_price=Decimal("1200000"),
        purchase_date=date(2024, 2, 1),
        weight_units=Decimal("5"),
        latest_unit_price=Decimal("240000"),
    )
    portfolio.add_asset(gold)

    cash = CashAsset(
        name="Savings Bank Balance",
        balance=Decimal("800000"),
        purchase_date=date(2024, 1, 1),
    )
    portfolio.add_asset(cash)

    assert portfolio.total_value() == Decimal("10000000")

    cat_shares = portfolio.category_shares()
    assert cat_shares["real_estate"] == Decimal("0.6")
    assert cat_shares["stocks"] == Decimal("0.2")
    assert cat_shares["gold"] == Decimal("0.12")
    assert cat_shares["cash"] == Decimal("0.08")

    hhi = RiskAnalyzer.calculate_hhi(cat_shares)
    assert hhi == Decimal("0.4208")

    largest_holding = RiskAnalyzer.calculate_largest_holding_share(portfolio)
    assert largest_holding == Decimal("0.4")
    assert portfolio.liquid_share() == Decimal("0.4")

    evaluator = AssetHealthEvaluator(ScoreSettings())
    result = evaluator.evaluate_portfolio(
        portfolio=portfolio,
        annualized_return_pct=Decimal("9.0"),
        growth_12m_pct=Decimal("6.0"),
        income_yield_pct=Decimal("1.6"),
    )

    assert result.profitability_score == Decimal("75.0")
    assert result.diversification_score == Decimal("72.4")
    assert result.hhi == Decimal("0.4208")
    assert result.liquidity_score == Decimal("80.0")
    assert result.risk_score == Decimal("50.0")
    assert result.growth_score == Decimal("60.0")
    assert result.income_score == Decimal("40.0")
    assert result.total_score == Decimal("65.73")
    assert result.band == "Moderately Healthy"


def test_asset_health_status_rules():
    """Verify per-asset health classifications: Weak, Watch, Healthy."""
    today = date(2026, 11, 23)

    weak_asset = Stock(
        name="Loss Stock",
        purchase_price=Decimal("100"),
        purchase_date=date(2025, 1, 1),
        quantity=Decimal("10"),
        latest_price=Decimal("70"),
    )
    assert AssetHealthStatus.evaluate(weak_asset, Decimal("100000"), as_of=today) == AssetHealthStatus.WEAK

    peak_drop_asset = Stock(
        name="Peak Dropper",
        purchase_price=Decimal("100"),
        purchase_date=date(2026, 8, 1),
        quantity=Decimal("10"),
        latest_price=Decimal("75"),
    )
    peak_drop_asset.add_valuation(date(2026, 9, 1), Decimal("1000"))
    assert AssetHealthStatus.evaluate(peak_drop_asset, Decimal("100000"), as_of=today) == AssetHealthStatus.WEAK

    outdated_val_asset = Land(
        name="Old Land",
        purchase_price=Decimal("500000"),
        purchase_date=date(2026, 1, 1),
    )
    outdated_val_asset.add_valuation(date(2026, 5, 1), Decimal("520000"))
    assert AssetHealthStatus.evaluate(outdated_val_asset, Decimal("10000000"), as_of=today) == AssetHealthStatus.WATCH

    healthy_asset = Stock(
        name="Healthy Stock",
        purchase_price=Decimal("100"),
        purchase_date=date(2026, 10, 1),
        quantity=Decimal("100"),
        latest_price=Decimal("110"),
    )
    healthy_asset.add_valuation(date(2026, 11, 1), Decimal("11000"))
    assert AssetHealthStatus.evaluate(healthy_asset, Decimal("1000000"), as_of=today) == AssetHealthStatus.HEALTHY
