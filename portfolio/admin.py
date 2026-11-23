"""Admin registration for portfolio models."""

from django.contrib import admin
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
    Transaction,
    Income,
    ScoreSetting,
    HealthAssessment,
    Alert,
    FinancialReport,
)

admin.site.register(Portfolio)
admin.site.register(Stock)
admin.site.register(Bond)
admin.site.register(Fund)
admin.site.register(CashAccount)
admin.site.register(Gold)
admin.site.register(RealEstate)
admin.site.register(AssetValuation)
admin.site.register(Transaction)
admin.site.register(Income)
admin.site.register(ScoreSetting)
admin.site.register(HealthAssessment)
admin.site.register(Alert)
admin.site.register(FinancialReport)
