"""Views for Portfolio dashboard, asset management, and valuations."""

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
    user = request.user
    portfolio = Portfolio.objects.filter(user=user).first()

    if not portfolio:
        portfolio = Portfolio.objects.create(
            user=user,
            name="Primary Portfolio",
            base_currency="PKR",
            is_default=True,
        )

    analytics_p, score_result, alerts, asset_cards = PortfolioAnalyticsBridge.evaluate(
        portfolio_model=portfolio,
        annualized_return_pct=Decimal("9.0"),
        growth_12m_pct=Decimal("6.0"),
        income_yield_pct=Decimal("1.6"),
    )

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
def asset_create_view(request, asset_type):
    """Form view to add a new physical or financial asset."""
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
            # Record initial valuation row matching purchase price or latest price
            initial_val = asset.cost_basis
            AssetValuation.objects.create(
                asset=asset,
                valuation_date=asset.purchase_date,
                value=initial_val,
                source=AssetValuation.Source.MANUAL,
                notes="Initial purchase valuation",
            )
            messages.success(request, f"{display_name} '{asset.name}' has been added successfully.")
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
    """View details, valuation history, and income logs for an asset."""
    asset = get_object_or_404(Asset, id=asset_id, portfolio__user=request.user)
    valuations = asset.valuations.all()
    incomes = asset.incomes.all()

    valuation_form = AssetValuationForm()
    income_form = IncomeForm()

    if request.method == "POST":
        if "submit_valuation" in request.POST:
            v_form = AssetValuationForm(request.POST)
            if v_form.is_valid():
                val = v_form.save(commit=False)
                val.asset = asset
                val.save()
                messages.success(request, f"New valuation of PKR {val.value} recorded.")
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
            "valuation_form": valuation_form,
            "income_form": income_form,
        },
    )
