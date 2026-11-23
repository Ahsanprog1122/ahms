"""Forms for Portfolio and Asset entry."""

from django import forms
from .models import (
    Portfolio,
    Stock,
    Bond,
    Fund,
    CashAccount,
    Gold,
    RealEstate,
    AssetValuation,
    Transaction,
    Income,
)


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ["name", "description", "base_currency"]


class AssetValuationForm(forms.ModelForm):
    class Meta:
        model = AssetValuation
        fields = ["valuation_date", "value", "source", "notes"]
        widgets = {
            "valuation_date": forms.DateInput(attrs={"type": "date"}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["transaction_type", "transaction_date", "quantity", "price_per_unit", "fees", "notes"]
        widgets = {
            "transaction_date": forms.DateInput(attrs={"type": "date"}),
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ["income_type", "amount", "received_date", "tax_deducted", "notes"]
        widgets = {
            "received_date": forms.DateInput(attrs={"type": "date"}),
        }
