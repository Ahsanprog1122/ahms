"""AHMS Analytics Package.

Pure Python OOP package for asset tracking, financial calculations,
risk assessment, and health evaluation. Zero Django dependencies.
All monetary calculations strictly use Decimal.
"""

from .base import (
    Asset,
    FinancialAsset,
    PhysicalAsset,
    AssetValuation,
    Transaction,
    IncomeRecord,
    Dividend,
    InterestIncome,
)
from .assets import (
    Stock,
    Bond,
    MutualFund,
    CashAsset,
    RealEstate,
    Land,
    Gold,
)
from .portfolio import Portfolio
from .analyzers import FinancialAnalyzer, RiskAnalyzer
from .evaluator import (
    AssetHealthEvaluator,
    HealthScoreResult,
    AssetHealthStatus,
    ScoreSettings,
)
from .recommendations import RecommendationEngine, Alert

__all__ = [
    "Asset",
    "FinancialAsset",
    "PhysicalAsset",
    "AssetValuation",
    "Transaction",
    "IncomeRecord",
    "Dividend",
    "InterestIncome",
    "Stock",
    "Bond",
    "MutualFund",
    "CashAsset",
    "RealEstate",
    "Land",
    "Gold",
    "Portfolio",
    "FinancialAnalyzer",
    "RiskAnalyzer",
    "AssetHealthEvaluator",
    "HealthScoreResult",
    "AssetHealthStatus",
    "ScoreSettings",
    "RecommendationEngine",
    "Alert",
]
