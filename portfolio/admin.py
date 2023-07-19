from django.contrib import admin
from .models import Portfolio, Asset, AssetBalance, AssetBalanceHistory, AssetPriceHistory, Exchange

# Register your models here.
admin.site.register(Exchange)
admin.site.register(AssetPriceHistory)

# Defining inlines
class AssetBalanceInline(admin.TabularInline):
    model = AssetBalance
    extra = 1

class AssetBalanceHistoryInline(admin.TabularInline):
    model = AssetBalanceHistory
    extra = 1

class AssetPriceHistoryInline(admin.TabularInline):
    model = AssetPriceHistory
    extra = 1


# Admin models
@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    inlines = [AssetBalanceInline]

@admin.register(AssetBalance)
class AssetBalanceAdmin(admin.ModelAdmin):
    # list_display = ('portfolio', 'currency')
    inlines = [AssetBalanceHistoryInline]

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    inlines = [AssetPriceHistoryInline]

