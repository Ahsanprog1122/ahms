"""portfolio models.

Implemented by Abdul Jabbar following AHMS specifications.
Strictly uses DecimalField for all monetary values.
Uses multi-table inheritance for Asset child models.
All queries are scoped to the authenticated user's portfolio.
"""

from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Portfolio(models.Model):
    """Container for a user's assets."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="portfolios",
        help_text="User who owns this portfolio.",
    )
    name = models.CharField(max_length=150, default="Primary Portfolio")
    description = models.TextField(blank=True, default="")
    base_currency = models.CharField(max_length=10, default="PKR")
    is_default = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "name"]
        verbose_name = "Portfolio"
        verbose_name_plural = "Portfolios"

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Asset(models.Model):
    """Parent model for all physical and financial assets.

    Uses Multi-Table Inheritance so concrete assets (Stock, Bond, RealEstate, etc.)
    get their own tables linked via an automatic OneToOneField.
    """

    class Category(models.TextChoices):
        STOCKS = "stocks", "Stocks / Equities"
        BONDS = "bonds", "Bonds / Fixed Income"
        FUNDS = "funds", "Mutual Funds / ETFs"
        CASH = "cash", "Cash & Bank Accounts"
        GOLD = "gold", "Gold & Precious Metals"
        REAL_ESTATE = "real_estate", "Real Estate & Land"
        VEHICLES = "vehicles", "Vehicles & Automobiles"
        OTHER = "other", "Other Physical Asset"

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    name = models.CharField(max_length=200, help_text="Descriptive asset name.")
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        help_text="Asset classification category.",
    )
    is_liquid = models.BooleanField(
        default=False,
        help_text="Whether this asset can be rapidly converted to cash without significant price discount.",
    )
    purchase_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Price per unit at purchase in PKR.",
    )
    purchase_date = models.DateField(help_text="Date of acquisition.")
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("1.0000"),
        validators=[MinValueValidator(Decimal("0.0001"))],
        help_text="Quantity or units owned.",
    )
    costs = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Initial transaction fees, commission, taxes, or registration costs in PKR.",
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-purchase_date", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    @property
    def cost_basis(self) -> Decimal:
        """Total cost basis = (purchase_price * quantity) + costs."""
        return (self.purchase_price * self.quantity) + self.costs

    def get_latest_valuation(self):
        """Returns the most recent valuation record or None."""
        return self.valuations.order_by("-valuation_date", "-id").first()

    def get_current_value(self) -> Decimal:
        """Fallback current value from latest valuation or cost basis."""
        latest = self.get_latest_valuation()
        if latest:
            return latest.value
        return self.cost_basis


# --- Child Asset Models (Financial Assets) ---

class Stock(Asset):
    """Listed equities holding."""

    ticker = models.CharField(max_length=20, help_text="PSX Ticker symbol (e.g. ENGRO, OGDC).")
    exchange = models.CharField(max_length=50, default="PSX")
    latest_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Latest market closing price per share.",
    )

    def save(self, *args, **kwargs):
        self.category = Asset.Category.STOCKS
        self.is_liquid = True
        super().save(*args, **kwargs)


class Bond(Asset):
    """Fixed-income security holding."""

    face_value = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Face value per certificate.",
    )
    price_percent = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        default=Decimal("100.000"),
        help_text="Clean price as % of face value (e.g. 100.000).",
    )
    accrued_interest = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Accrued interest since last coupon payment.",
    )
    coupon_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Annual coupon rate percentage (e.g. 15.50 for 15.5%).",
    )
    maturity_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.category = Asset.Category.BONDS
        self.is_liquid = True
        super().save(*args, **kwargs)


class Fund(Asset):
    """Mutual Fund or ETF holding."""

    fund_code = models.CharField(max_length=50, blank=True, default="")
    fund_manager = models.CharField(max_length=150, blank=True, default="")
    latest_nav = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Latest Net Asset Value per unit.",
    )

    def save(self, *args, **kwargs):
        self.category = Asset.Category.FUNDS
        self.is_liquid = True
        super().save(*args, **kwargs)


class CashAccount(Asset):
    """Bank deposits, savings accounts, or physical cash."""

    bank_name = models.CharField(max_length=150, blank=True, default="")
    account_number = models.CharField(max_length=50, blank=True, default="")
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Annual savings interest / profit rate.",
    )

    def save(self, *args, **kwargs):
        self.category = Asset.Category.CASH
        self.is_liquid = True
        super().save(*args, **kwargs)


# --- Child Asset Models (Physical Assets) ---

class Gold(Asset):
    """Gold bullion, coins, or jewelry."""

    unit_type = models.CharField(
        max_length=20,
        choices=[("tola", "Tola"), ("gram", "Gram"), ("ounce", "Ounce")],
        default="tola",
    )
    purity = models.CharField(max_length=20, default="24K")
    latest_unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Latest market price per unit (e.g. per tola).",
    )

    def save(self, *args, **kwargs):
        self.category = Asset.Category.GOLD
        self.is_liquid = True  # Liquid in AHMS rules
        super().save(*args, **kwargs)


class RealEstate(Asset):
    """Physical plots, houses, commercial buildings."""

    class PropertyType(models.TextChoices):
        LAND = "land", "Vacant Land / Plot"
        RESIDENTIAL = "residential", "Residential House / Apartment"
        COMMERCIAL = "commercial", "Commercial Building / Shop"
        AGRICULTURAL = "agricultural", "Agricultural Land"

    property_type = models.CharField(
        max_length=30,
        choices=PropertyType.choices,
        default=PropertyType.LAND,
    )
    area_size = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1.00"),
    )
    area_unit = models.CharField(
        max_length=20,
        choices=[("marla", "Marla"), ("kanal", "Kanal"), ("sqft", "Sq. Ft"), ("acre", "Acre")],
        default="marla",
    )
    location = models.CharField(max_length=255, blank=True, default="")

    def save(self, *args, **kwargs):
        self.category = Asset.Category.REAL_ESTATE
        self.is_liquid = False
        super().save(*args, **kwargs)


# --- Supporting Tracking Records (Append-Only) ---

class AssetValuation(models.Model):
    """Historical valuation entry.

    Rule: Never overwrite an existing valuation; always add a new row.
    """

    class Source(models.TextChoices):
        MANUAL = "manual", "Manual Entry"
        API = "api", "Market Data API"
        APPRAISAL = "appraisal", "Certified Appraisal"

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="valuations",
    )
    valuation_date = models.DateField(help_text="Date of valuation record.")
    value = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Total market value of the asset at this date in PKR.",
    )
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.MANUAL,
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-valuation_date", "-id"]
        verbose_name = "Asset Valuation"
        verbose_name_plural = "Asset Valuations"

    def __str__(self):
        return f"{self.asset.name} - {self.value} PKR ({self.valuation_date})"


class Transaction(models.Model):
    """Buy, Sell, or Expense transaction log."""

    class TxType(models.TextChoices):
        BUY = "buy", "Purchase"
        SELL = "sell", "Sale"
        EXPENSE = "expense", "Capital / Maintenance Expense"

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    transaction_type = models.CharField(max_length=20, choices=TxType.choices)
    transaction_date = models.DateField()
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0.0001"))],
    )
    price_per_unit = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    fees = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-transaction_date", "-id"]

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.quantity} of {self.asset.name}"


class Income(models.Model):
    """Income received from an asset (Dividends, Interest, Rent)."""

    class IncomeType(models.TextChoices):
        DIVIDEND = "dividend", "Dividend"
        INTEREST = "interest", "Interest / Profit"
        RENT = "rent", "Rental Income"
        OTHER = "other", "Other Yield"

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="incomes",
    )
    income_type = models.CharField(max_length=20, choices=IncomeType.choices)
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Income amount in PKR.",
    )
    received_date = models.DateField()
    tax_deducted = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-received_date", "-id"]

    def __str__(self):
        return f"{self.get_income_type_display()} PKR {self.amount} ({self.received_date})"


# --- Health Scoring, Settings & Reports ---

class ScoreSetting(models.Model):
    """Configurable weights and limits for portfolio health calculation."""

    portfolio = models.OneToOneField(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="score_setting",
    )
    weight_profitability = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal("0.25"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("1.00"))],
    )
    weight_diversification = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal("0.20"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("1.00"))],
    )
    weight_liquidity = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal("0.15"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("1.00"))],
    )
    weight_risk = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal("0.15"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("1.00"))],
    )
    weight_growth = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal("0.15"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("1.00"))],
    )
    weight_income = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal("0.10"),
        validators=[MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("1.00"))],
    )

    def __str__(self):
        return f"ScoreSetting for {self.portfolio.name}"


class HealthAssessment(models.Model):
    """Snapshot of portfolio health score evaluation."""

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="health_assessments",
    )
    assessment_date = models.DateField(auto_now_add=True)
    total_score = models.DecimalField(max_digits=5, decimal_places=2)
    band = models.CharField(max_length=50)  # Healthy, Moderately Healthy, Needs Improvement, Financially Weak

    profitability_score = models.DecimalField(max_digits=5, decimal_places=2)
    diversification_score = models.DecimalField(max_digits=5, decimal_places=2)
    liquidity_score = models.DecimalField(max_digits=5, decimal_places=2)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2)
    growth_score = models.DecimalField(max_digits=5, decimal_places=2)
    income_score = models.DecimalField(max_digits=5, decimal_places=2)

    hhi = models.DecimalField(max_digits=7, decimal_places=4)
    largest_holding_share = models.DecimalField(max_digits=5, decimal_places=4)
    liquid_share = models.DecimalField(max_digits=5, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.portfolio.name}: {self.total_score}/100 ({self.band}) on {self.assessment_date}"


class Alert(models.Model):
    """Decision-support alert associated with a health assessment."""

    assessment = models.ForeignKey(
        HealthAssessment,
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    severity = models.CharField(
        max_length=20,
        choices=[("high", "High"), ("medium", "Medium"), ("low", "Low"), ("info", "Info")],
        default="medium",
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    recommendation = models.TextField()
    is_dismissed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"


class FinancialReport(models.Model):
    """Archived PDF or CSV report generation record."""

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    report_type = models.CharField(
        max_length=20,
        choices=[("pdf", "PDF Document"), ("csv", "CSV Spreadsheet")],
    )
    title = models.CharField(max_length=200)
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=500, blank=True, default="")

    def __str__(self):
        return f"{self.title} ({self.report_type.upper()}) - {self.generated_at.date()}"
