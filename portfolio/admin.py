from django.contrib import admin
from .models import Portfolio, Asset, AssetBalance, AssetBalanceHistory

# Register your models here.
admin.site.register(Asset)

# Defining inlines
class AssetBalanceInline(admin.TabularInline):
    model = AssetBalance
    extra = 1

class AssetBalanceHistoryInline(admin.TabularInline):
    model = AssetBalanceHistory
    extra = 1


# Admin models
@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    inlines = [AssetBalanceInline]

@admin.register(AssetBalance)
class CashAdmin(admin.ModelAdmin):
    # list_display = ('portfolio', 'currency')
    inlines = [AssetBalanceHistoryInline]

