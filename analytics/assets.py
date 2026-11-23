"""Concrete asset classes for the AHMS Analytics Engine.

Subclasses inherit from FinancialAsset or PhysicalAsset and implement current_value().
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from .base import FinancialAsset, PhysicalAsset


class Stock(FinancialAsset):
    """Stock / Equity holding."""

    def __init__(
        self,
        name: str,
        purchase_price: Decimal,
        purchase_date: date,
        quantity: Decimal,
        ticker: str = "",
        latest_price: Optional[Decimal] = None,
        costs: Decimal = Decimal("0"),
        asset_id: Optional[str] = None,
    ):
        super().__init__(name, purchase_price, purchase_date, quantity, costs, asset_id)
        self.ticker = ticker
        self.latest_price = Decimal(str(latest_price)) if latest_price is not None else self.purchase_price

    @property
    def category(self) -> str:
        return "stocks"

    def current_value(self) -> Decimal:
        """Current value = quantity * latest_price."""
        return self.quantity * self.latest_price


class Bond(FinancialAsset):
    """Bond / Fixed-Income security."""

    def __init__(
        self,
        name: str,
        purchase_price: Decimal,
        purchase_date: date,
        quantity: Decimal,
        face_value: Decimal,
        price_percent: Decimal = Decimal("100"),
        accrued_interest: Decimal = Decimal("0"),
        coupon_rate: Decimal = Decimal("0"),
        maturity_date: Optional[date] = None,
        costs: Decimal = Decimal("0"),
        asset_id: Optional[str] = None,
    ):
        super().__init__(name, purchase_price, purchase_date, quantity, costs, asset_id)
        self.face_value = Decimal(str(face_value))
        self.price_percent = Decimal(str(price_percent))
        self.accrued_interest = Decimal(str(accrued_interest))
        self.coupon_rate = Decimal(str(coupon_rate))
        self.maturity_date = maturity_date

    @property
    def category(self) -> str:
        return "bonds"

    def current_value(self) -> Decimal:
        clean_value = self.quantity * self.face_value * (self.price_percent / Decimal("100"))
        return clean_value + self.accrued_interest


class MutualFund(FinancialAsset):
    """Mutual Fund or ETF holding."""

    def __init__(
        self,
        name: str,
        purchase_price: Decimal,
        purchase_date: date,
        quantity: Decimal,
        latest_nav: Optional[Decimal] = None,
        fund_code: str = "",
        costs: Decimal = Decimal("0"),
        asset_id: Optional[str] = None,
    ):
        super().__init__(name, purchase_price, purchase_date, quantity, costs, asset_id)
        self.fund_code = fund_code
        self.latest_nav = Decimal(str(latest_nav)) if latest_nav is not None else self.purchase_price

    @property
    def category(self) -> str:
        return "mutual_funds"

    def current_value(self) -> Decimal:
        return self.quantity * self.latest_nav


class CashAsset(FinancialAsset):
    """Cash, bank deposits, savings accounts."""

    def __init__(
        self,
        name: str,
        balance: Decimal,
        purchase_date: Optional[date] = None,
        interest_rate: Decimal = Decimal("0"),
        costs: Decimal = Decimal("0"),
        asset_id: Optional[str] = None,
    ):
        p_date = purchase_date or date.today()
        super().__init__(name, purchase_price=balance, purchase_date=p_date, quantity=Decimal("1"), costs=costs, asset_id=asset_id)
        self.balance = Decimal(str(balance))
        self.interest_rate = Decimal(str(interest_rate))

    @property
    def category(self) -> str:
        return "cash"

    def current_value(self) -> Decimal:
        return self.balance


class Gold(PhysicalAsset):
    """Gold bullion or jewelry."""

    def __init__(
        self,
        name: str,
        purchase_price: Decimal,
        purchase_date: date,
        weight_units: Decimal,
        latest_unit_price: Optional[Decimal] = None,
        unit_type: str = "tola",
        costs: Decimal = Decimal("0"),
        asset_id: Optional[str] = None,
    ):
        super().__init__(name, purchase_price, purchase_date, quantity=weight_units, costs=costs, asset_id=asset_id)
        self.unit_type = unit_type
        self.latest_unit_price = Decimal(str(latest_unit_price)) if latest_unit_price is not None else (self.purchase_price / weight_units if weight_units else Decimal("0"))

    @property
    def category(self) -> str:
        return "gold"

    @property
    def is_liquid(self) -> bool:
        return True

    def current_value(self) -> Decimal:
        return self.quantity * self.latest_unit_price


class Land(PhysicalAsset):
    """Land holding."""

    def __init__(
        self,
        name: str,
        purchase_price: Decimal,
        purchase_date: date,
        area_size: Decimal = Decimal("1"),
        area_unit: str = "kanal",
        costs: Decimal = Decimal("0"),
        asset_id: Optional[str] = None,
    ):
        super().__init__(name, purchase_price, purchase_date, quantity=area_size, costs=costs, asset_id=asset_id)
        self.area_unit = area_unit

    @property
    def category(self) -> str:
        return "real_estate"

    def current_value(self) -> Decimal:
        latest = self.latest_valuation()
        if latest:
            return latest.value
        return self.total_cost_basis()


class RealEstate(PhysicalAsset):
    """Constructed residential/commercial property."""

    def __init__(
        self,
        name: str,
        purchase_price: Decimal,
        purchase_date: date,
        property_type: str = "residential",
        costs: Decimal = Decimal("0"),
        asset_id: Optional[str] = None,
    ):
        super().__init__(name, purchase_price, purchase_date, quantity=Decimal("1"), costs=costs, asset_id=asset_id)
        self.property_type = property_type

    @property
    def category(self) -> str:
        return "real_estate"

    def current_value(self) -> Decimal:
        latest = self.latest_valuation()
        if latest:
            return latest.value
        return self.total_cost_basis()
