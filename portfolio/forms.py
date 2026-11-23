"""Forms for adding and editing physical and financial assets."""

from django import forms
from .models import (
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


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ["name", "ticker", "exchange", "purchase_price", "purchase_date", "quantity", "latest_price", "costs", "notes"]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
        }


class BondForm(forms.ModelForm):
    class Meta:
        model = Bond
        fields = ["name", "face_value", "price_percent", "accrued_interest", "coupon_rate", "maturity_date", "purchase_price", "purchase_date", "quantity", "costs", "notes"]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "maturity_date": forms.DateInput(attrs={"type": "date"}),
        }


class FundForm(forms.ModelForm):
    class Meta:
        model = Fund
        fields = ["name", "fund_code", "fund_manager", "purchase_price", "purchase_date", "quantity", "latest_nav", "costs", "notes"]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
        }


class CashAccountForm(forms.ModelForm):
    class Meta:
        model = CashAccount
        fields = ["name", "bank_name", "account_number", "purchase_price", "purchase_date", "interest_rate", "costs", "notes"]
        labels = {
            "purchase_price": "Cash Balance (PKR)",
        }
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
        }


class GoldForm(forms.ModelForm):
    class Meta:
        model = Gold
        fields = ["name", "unit_type", "purity", "quantity", "purchase_price", "purchase_date", "latest_unit_price", "costs", "notes"]
        labels = {
            "quantity": "Weight Units (e.g. Tolas / Grams)",
            "purchase_price": "Total Purchase Amount (PKR)",
        }
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
        }


class RealEstateForm(forms.ModelForm):
    class Meta:
        model = RealEstate
        fields = ["name", "property_type", "area_size", "area_unit", "location", "purchase_price", "purchase_date", "costs", "notes"]
        labels = {
            "purchase_price": "Acquisition Price (PKR)",
        }
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
        }


class AssetValuationForm(forms.ModelForm):
    class Meta:
        model = AssetValuation
        fields = ["valuation_date", "value", "source", "notes"]
        widgets = {
            "valuation_date": forms.DateInput(attrs={"type": "date"}),
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ["income_type", "amount", "received_date", "tax_deducted", "notes"]
        widgets = {
            "received_date": forms.DateInput(attrs={"type": "date"}),
        }
