"""Views for all proposal screens."""

from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Portfolio,
    Asset,
    Stock,
    Bond,
    Fund,
    CashAccount,
    Gold,
    RealEstate,
    AssetValuation,
    Income,
)
from .bridge import PortfolioAnalyticsBridge
from .forms import (
    StockForm,
    BondForm,
    FundForm,
    CashAccountForm,
    GoldForm,
    RealEstateForm,
    AssetValuationForm,
    IncomeForm,
)


@login_required
def dashboard_view(request):
    """Primary Portfolio Dashboard showing Health Score, Asset Allocation, and Alerts."""
    portfolio = Portfolio.objects.filter(user=request.user).first()
    if not portfolio:
        portfolio = Portfolio.objects.create(user=request.user, name="Primary Portfolio")

    analytics_p, score_result, alerts, asset_cards = PortfolioAnalyticsBridge.evaluate(portfolio)
    cat_shares = analytics_p.category_shares()
    chart_labels = [cat.replace("_", " ").title() for cat in cat_shares.keys()]
    chart_data = [float(val * Decimal("100")) for val in cat_shares.values()]

    return render(
        request,
        "portfolio/dashboard.html",
        {
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
        },
    )


@login_required
def asset_list_view(request):
    """Screen: Assets Inventory (Proposal Page 15)."""
    portfolio = Portfolio.objects.filter(user=request.user).first()
    assets = portfolio.assets.all() if portfolio else []

    analytics_p, score_result, alerts, asset_cards = PortfolioAnalyticsBridge.evaluate(portfolio) if portfolio else (None, None, [], [])

    asset_rows = []
    if portfolio:
        for a in assets:
            current_val = a.get_current_value()
            gain = current_val - a.cost_basis
            status = "Healthy"
            if a.valuations.exists() and (a.get_latest_valuation().valuation_date):
                from datetime import date
                if (date.today() - a.get_latest_valuation().valuation_date).days > 90:
                    status = "Watch"
            asset_rows.append({
                "asset": a,
                "current_val": current_val,
                "gain": gain,
                "status": status,
            })

    return render(request, "portfolio/asset_list.html", {"portfolio": portfolio, "asset_rows": asset_rows})


@login_required
def portfolio_analysis_view(request):
    """Screen: Portfolio Analysis (Proposal Page 16)."""
    portfolio = Portfolio.objects.filter(user=request.user).first()
    analytics_p, score_result, alerts, asset_cards = PortfolioAnalyticsBridge.evaluate(portfolio)

    cat_shares = analytics_p.category_shares()
    chart_labels = [cat.replace("_", " ").title() for cat in cat_shares.keys()]
    chart_data = [float(val * Decimal("100")) for val in cat_shares.values()]
    cat_share_items = [(cat.replace("_", " "), float(val * Decimal("100"))) for cat, val in cat_shares.items()]

    return render(
        request,
        "portfolio/portfolio_analysis.html",
        {
            "portfolio": portfolio,
            "total_value": analytics_p.total_value(),
            "score_result": score_result,
            "asset_cards": asset_cards,
            "chart_labels": chart_labels,
            "chart_data": chart_data,
            "cat_share_items": cat_share_items,
        },
    )


@login_required
def health_score_detail_view(request):
    """Screen: Health Score Breakdown (Proposal Page 16)."""
    portfolio = Portfolio.objects.filter(user=request.user).first()
    analytics_p, score_result, alerts, asset_cards = PortfolioAnalyticsBridge.evaluate(portfolio)

    return render(
        request,
        "portfolio/health_score_detail.html",
        {
            "portfolio": portfolio,
            "score_result": score_result,
        },
    )


@login_required
def alerts_list_view(request):
    """Screen: Recommendations and Alerts (Proposal Page 16)."""
    portfolio = Portfolio.objects.filter(user=request.user).first()
    analytics_p, score_result, alerts, asset_cards = PortfolioAnalyticsBridge.evaluate(portfolio)

    return render(
        request,
        "portfolio/alerts_list.html",
        {
            "portfolio": portfolio,
            "alerts": alerts,
        },
    )


@login_required
def reports_view(request):
    """Screen: Reports Download PDF/CSV (Proposal Page 16)."""
    portfolio = Portfolio.objects.filter(user=request.user).first()
    return render(request, "reports/reports_view.html", {"portfolio": portfolio})


@login_required
def settings_view(request):
    """Screen: Settings and Data Privacy Controls (Proposal Page 16-18)."""
    portfolio = Portfolio.objects.filter(user=request.user).first()
    return render(request, "portfolio/settings_view.html", {"portfolio": portfolio})


@login_required
def asset_create_view(request, asset_type):
    """Screen: Add or Edit Asset (Proposal Page 16)."""
    portfolio = Portfolio.objects.filter(user=request.user).first()
    if not portfolio:
        portfolio = Portfolio.objects.create(user=request.user, name="Primary Portfolio")

    form_mapping = {
        "stock": (StockForm, "Stock"),
        "bond": (BondForm, "Bond"),
        "fund": (FundForm, "Mutual Fund / ETF"),
        "cash": (CashAccountForm, "Cash / Bank Deposit"),
        "gold": (GoldForm, "Gold"),
        "realestate": (RealEstateForm, "Real Estate / Land"),
    }

    if asset_type not in form_mapping:
        messages.error(request, "Invalid asset type selected.")
        return redirect("dashboard")

    form_class, display_name = form_mapping[asset_type]

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.portfolio = portfolio
            asset.save()
            AssetValuation.objects.create(
                asset=asset,
                valuation_date=asset.purchase_date,
                value=asset.cost_basis,
                source=AssetValuation.Source.MANUAL,
                notes="Initial acquisition valuation",
            )
            messages.success(request, f"{display_name} '{asset.name}' recorded successfully.")
            return redirect("dashboard")
    else:
        form = form_class()

    return render(
        request,
        "portfolio/asset_form.html",
        {
            "form": form,
            "display_name": display_name,
            "asset_type": asset_type,
            "portfolio": portfolio,
        },
    )


@login_required
def asset_detail_view(request, asset_id):
    """Screen: Asset Detail & Update Valuation (Proposal Page 16)."""
    asset = get_object_or_404(Asset, id=asset_id, portfolio__user=request.user)
    valuations = asset.valuations.all()
    incomes = asset.incomes.all()

    if request.method == "POST":
        if "submit_valuation" in request.POST:
            v_form = AssetValuationForm(request.POST)
            if v_form.is_valid():
                val = v_form.save(commit=False)
                val.asset = asset
                val.save()
                messages.success(request, f"New valuation of PKR {val.value} added to history.")
                return redirect("asset_detail", asset_id=asset.id)
        elif "submit_income" in request.POST:
            i_form = IncomeForm(request.POST)
            if i_form.is_valid():
                inc = i_form.save(commit=False)
                inc.asset = asset
                inc.save()
                messages.success(request, f"Income of PKR {inc.amount} recorded.")
                return redirect("asset_detail", asset_id=asset.id)

    return render(
        request,
        "portfolio/asset_detail.html",
        {
            "asset": asset,
            "valuations": valuations,
            "incomes": incomes,
            "valuation_form": AssetValuationForm(),
            "income_form": IncomeForm(),
        },
    )
