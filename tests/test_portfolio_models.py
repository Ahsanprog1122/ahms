"""Tests for portfolio models, multi-table inheritance, and tenant isolation."""

from datetime import date
from decimal import Decimal
import pytest
from django.contrib.auth.models import User
from portfolio.models import (
    Portfolio,
    Stock,
    Bond,
    Gold,
    RealEstate,
    CashAccount,
    AssetValuation,
    Transaction,
    Income,
    ScoreSetting,
)


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username="investor1",
        email="inv1@ahms.internal",
        password="Password123!",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="investor2",
        email="inv2@ahms.internal",
        password="Password123!",
    )


@pytest.fixture
def portfolio(test_user):
    return Portfolio.objects.create(
        user=test_user,
        name="Main Investment Portfolio",
    )


@pytest.mark.django_db
def test_stock_creation_and_inheritance(portfolio):
    """Test Stock model multi-table inheritance and properties."""
    stock = Stock.objects.create(
        portfolio=portfolio,
        name="Engro Corporation",
        ticker="ENGRO",
        purchase_price=Decimal("300.00"),
        purchase_date=date(2025, 1, 15),
        quantity=Decimal("1000.0000"),
        latest_price=Decimal("320.00"),
        costs=Decimal("500.00"),
    )

    assert stock.category == "stocks"
    assert stock.is_liquid is True
    # Cost basis = (300 * 1000) + 500 = 300,500
    assert stock.cost_basis == Decimal("300500.00")
    assert stock.get_current_value() == Decimal("300500.00")


@pytest.mark.django_db
def test_valuation_append_only(portfolio):
    """Valuations are append-only; latest returns most recent."""
    real_estate = RealEstate.objects.create(
        portfolio=portfolio,
        name="DHA Phase 6 Plot",
        purchase_price=Decimal("15000000.00"),
        purchase_date=date(2023, 1, 1),
        property_type=RealEstate.PropertyType.LAND,
        area_size=Decimal("1.00"),
        area_unit="kanal",
    )

    # Initially falls back to cost basis
    assert real_estate.get_current_value() == Decimal("15000000.00")

    # Add valuation 1
    AssetValuation.objects.create(
        asset=real_estate,
        valuation_date=date(2024, 1, 1),
        value=Decimal("17000000.00"),
        source=AssetValuation.Source.MANUAL,
    )
    assert real_estate.get_current_value() == Decimal("17000000.00")

    # Add valuation 2 (newer)
    AssetValuation.objects.create(
        asset=real_estate,
        valuation_date=date(2025, 1, 1),
        value=Decimal("19500000.00"),
        source=AssetValuation.Source.APPRAISAL,
    )
    assert real_estate.get_current_value() == Decimal("19500000.00")
    assert real_estate.valuations.count() == 2


@pytest.mark.django_db
def test_user_tenant_isolation(test_user, other_user, portfolio):
    """User A cannot access or query User B's portfolios or assets."""
    other_portfolio = Portfolio.objects.create(
        user=other_user,
        name="Other User Portfolio",
    )
    Stock.objects.create(
        portfolio=other_portfolio,
        name="Secret Asset",
        ticker="SEC",
        purchase_price=Decimal("100.00"),
        purchase_date=date(2025, 1, 1),
        quantity=Decimal("50.0000"),
    )

    # Scoped query for test_user should ONLY return test_user's portfolio
    user1_portfolios = Portfolio.objects.filter(user=test_user)
    assert portfolio in user1_portfolios
    assert other_portfolio not in user1_portfolios

    # Scoped assets query
    user1_assets = portfolio.assets.all()
    assert not user1_assets.filter(name="Secret Asset").exists()


@pytest.mark.django_db
def test_score_setting_defaults(portfolio):
    """Score settings have default weights summing to 1.00."""
    setting = ScoreSetting.objects.create(portfolio=portfolio)
    total_weights = (
        setting.weight_profitability
        + setting.weight_diversification
        + setting.weight_liquidity
        + setting.weight_risk
        + setting.weight_growth
        + setting.weight_income
    )
    assert total_weights == Decimal("1.00")
