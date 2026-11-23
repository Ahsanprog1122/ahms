"""Service adapter converting Django portfolio models into pure Analytics instances.

Ensures views and templates never perform financial calculations directly.
"""

from decimal import Decimal
from typing import Tuple, List
from django.db.models import QuerySet
from portfolio.models import (
    Portfolio as PortfolioModel,
    Asset as AssetModel,
    Stock as StockModel,
    Bond as BondModel,
    Fund as FundModel,
    CashAccount as CashAccountModel,
    Gold as GoldModel,
    RealEstate as RealEstateModel,
    ScoreSetting as ScoreSettingModel,
)
from analytics import (
    Portfolio as AnalyticsPortfolio,
    Stock as AnalyticsStock,
    Bond as AnalyticsBond,
    MutualFund as AnalyticsMutualFund,
    CashAsset as AnalyticsCashAsset,
    Gold as AnalyticsGold,
    RealEstate as AnalyticsRealEstate,
    Land as AnalyticsLand,
    AssetHealthEvaluator,
    HealthScoreResult,
    AssetHealthStatus,
    ScoreSettings as AnalyticsScoreSettings,
    RecommendationEngine,
    Alert as AnalyticsAlert,
)


class PortfolioAnalyticsBridge:
    """Bridges Django ORM portfolio objects with pure Analytics engine."""

    @classmethod
    def to_analytics_portfolio(cls, portfolio_model: PortfolioModel) -> AnalyticsPortfolio:
        analytics_p = AnalyticsPortfolio(
            name=portfolio_model.name,
            portfolio_id=str(portfolio_model.id),
        )

        assets = portfolio_model.assets.all().select_related(
            "stock", "bond", "fund", "cashaccount", "gold", "realestate"
        ).prefetch_related("valuations", "incomes")

        for asset_m in assets:
            a_obj = cls._convert_asset(asset_m)
            if a_obj:
                # Add historical valuations
                for val in asset_m.valuations.all():
                    a_obj.add_valuation(
                        valuation_date=val.valuation_date,
                        value=val.value,
                        source=val.source,
                        notes=val.notes,
                    )
                # Add historical income records
                for inc in asset_m.incomes.all():
                    from analytics.base import IncomeRecord
                    a_obj.income_records.append(
                        IncomeRecord(
                            record_date=inc.received_date,
                            amount=inc.amount,
                            income_type=inc.income_type,
                            notes=inc.notes,
                        )
                    )
                analytics_p.add_asset(a_obj)

        return analytics_p

    @classmethod
    def _convert_asset(cls, asset_m: AssetModel):
        if hasattr(asset_m, "stock"):
            st = asset_m.stock
            return AnalyticsStock(
                name=st.name,
                purchase_price=st.purchase_price,
                purchase_date=st.purchase_date,
                quantity=st.quantity,
                ticker=st.ticker,
                latest_price=st.latest_price or st.purchase_price,
                costs=st.costs,
                asset_id=str(st.id),
            )
        elif hasattr(asset_m, "bond"):
            bd = asset_m.bond
            return AnalyticsBond(
                name=bd.name,
                purchase_price=bd.purchase_price,
                purchase_date=bd.purchase_date,
                quantity=bd.quantity,
                face_value=bd.face_value,
                price_percent=bd.price_percent,
                accrued_interest=bd.accrued_interest,
                coupon_rate=bd.coupon_rate,
                maturity_date=bd.maturity_date,
                costs=bd.costs,
                asset_id=str(bd.id),
            )
        elif hasattr(asset_m, "fund"):
            fd = asset_m.fund
            return AnalyticsMutualFund(
                name=fd.name,
                purchase_price=fd.purchase_price,
                purchase_date=fd.purchase_date,
                quantity=fd.quantity,
                latest_nav=fd.latest_nav or fd.purchase_price,
                fund_code=fd.fund_code,
                costs=fd.costs,
                asset_id=str(fd.id),
            )
        elif hasattr(asset_m, "cashaccount"):
            ca = asset_m.cashaccount
            return AnalyticsCashAsset(
                name=ca.name,
                balance=ca.purchase_price,
                purchase_date=ca.purchase_date,
                interest_rate=ca.interest_rate,
                costs=ca.costs,
                asset_id=str(ca.id),
            )
        elif hasattr(asset_m, "gold"):
            gd = asset_m.gold
            return AnalyticsGold(
                name=gd.name,
                purchase_price=gd.purchase_price,
                purchase_date=gd.purchase_date,
                weight_units=gd.quantity,
                latest_unit_price=gd.latest_unit_price,
                unit_type=gd.unit_type,
                costs=gd.costs,
                asset_id=str(gd.id),
            )
        elif hasattr(asset_m, "realestate"):
            re = asset_m.realestate
            if re.property_type == RealEstateModel.PropertyType.LAND:
                return AnalyticsLand(
                    name=re.name,
                    purchase_price=re.purchase_price,
                    purchase_date=re.purchase_date,
                    area_size=re.area_size,
                    area_unit=re.area_unit,
                    costs=re.costs,
                    asset_id=str(re.id),
                )
            return AnalyticsRealEstate(
                name=re.name,
                purchase_price=re.purchase_price,
                purchase_date=re.purchase_date,
                property_type=re.property_type,
                costs=re.costs,
                asset_id=str(re.id),
            )
        return None

    @classmethod
    def evaluate(
        cls,
        portfolio_model: PortfolioModel,
        annualized_return_pct: Decimal = Decimal("9.0"),
        growth_12m_pct: Decimal = Decimal("6.0"),
        income_yield_pct: Decimal = Decimal("1.6"),
    ) -> Tuple[AnalyticsPortfolio, HealthScoreResult, List[AnalyticsAlert], List[dict]]:
        analytics_p = cls.to_analytics_portfolio(portfolio_model)

        # Build ScoreSettings from DB if available
        settings_obj = AnalyticsScoreSettings()
        if hasattr(portfolio_model, "score_setting"):
            ss = portfolio_model.score_setting
            settings_obj.weight_profitability = ss.weight_profitability
            settings_obj.weight_diversification = ss.weight_diversification
            settings_obj.weight_liquidity = ss.weight_liquidity
            settings_obj.weight_risk = ss.weight_risk
            settings_obj.weight_growth = ss.weight_growth
            settings_obj.weight_income = ss.weight_income

        evaluator = AssetHealthEvaluator(settings_obj)
        score_result = evaluator.evaluate_portfolio(
            portfolio=analytics_p,
            annualized_return_pct=annualized_return_pct,
            growth_12m_pct=growth_12m_pct,
            income_yield_pct=income_yield_pct,
        )

        alerts = RecommendationEngine.generate_recommendations(analytics_p, score_result)

        # Asset items decorated with status
        total_val = analytics_p.total_value()
        asset_cards = []
        for a in analytics_p.assets:
            status = AssetHealthStatus.evaluate(a, total_val)
            asset_cards.append({
                "name": a.name,
                "category": a.category,
                "is_liquid": a.is_liquid,
                "cost_basis": a.total_cost_basis(),
                "current_value": a.current_value(),
                "gain": a.gain(),
                "status": status,
            })

        return analytics_p, score_result, alerts, asset_cards
