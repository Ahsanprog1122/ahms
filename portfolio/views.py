"""Views for Portfolio dashboard, asset management, and valuations."""

from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Portfolio, Asset, AssetValuation
from .bridge import PortfolioAnalyticsBridge
from .forms import PortfolioForm, AssetValuationForm


@login_required
def dashboard_view(request):
    """Primary Portfolio Dashboard showing Health Score, Asset Allocation, and Alerts."""
    user = request.user
    portfolio = Portfolio.objects.filter(user=user).first()

    if not portfolio:
        portfolio = Portfolio.objects.create(
            user=user,
            name="Primary Portfolio",
            base_currency="PKR",
            is_default=True,
        )

    # Use analytics bridge to compute metrics (zero money math in view)
    analytics_p, score_result, alerts, asset_cards = PortfolioAnalyticsBridge.evaluate(
        portfolio_model=portfolio,
        annualized_return_pct=Decimal("9.0"),
        growth_12m_pct=Decimal("6.0"),
        income_yield_pct=Decimal("1.6"),
    )

    # Chart.js data
    cat_shares = analytics_p.category_shares()
    chart_labels = [cat.replace("_", " ").title() for cat in cat_shares.keys()]
    chart_data = [float(val * Decimal("100")) for val in cat_shares.values()]

    context = {
        "portfolio": portfolio,
        "total_value": analytics_p.total_value(),
        "cost_basis": analytics_p.total_cost_basis(),
        "total_gain": analytics_p.total_gain(),
        "score_result": score_result,
        "alerts": alerts,
        "asset_cards": asset_cards,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "base_currency": portfolio.base_currency,
    }

    return render(request, "portfolio/dashboard.html", context)


@login_required
def asset_list_view(request):
    """Listing of all assets in user's active portfolio."""
    portfolio = get_object_or_404(Portfolio, user=request.user, is_default=True)
    assets = portfolio.assets.all().select_related("stock", "bond", "fund", "cashaccount", "gold", "realestate")
    return render(request, "portfolio/asset_list.html", {"portfolio": portfolio, "assets": assets})
