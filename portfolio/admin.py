from django.contrib import admin
from .models import Portfolio, Asset, AssetBalance, AssetBalanceHistory, AssetPriceHistory, Exchange, ApiConnection

# Register your models here.
admin.site.register(ApiConnection)

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

class ApiConnectionInline(admin.TabularInline):
    model = ApiConnection
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
    pass
    # inlines = [AssetPriceHistoryInline]

@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    inlines = [ApiConnectionInline]

@admin.register(AssetPriceHistory)
class AssetPriceHistoryAdmin(admin.ModelAdmin):
    list_filter = ('asset', 'date')
    list_display = ('asset', 'date', 'price')

