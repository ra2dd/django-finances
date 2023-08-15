from django.contrib import admin
from .models import Portfolio, Asset, AssetBalance, AssetBalanceHistory, AssetPriceHistory, Exchange, ApiConnection

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
    inlines = [AssetBalanceHistoryInline]

    list_display = ('portfolio', 'asset', 'broker')
    list_filter = ['portfolio', ('asset', admin.RelatedOnlyFieldListFilter), 'broker']

@admin.register(AssetBalanceHistory)
class AssetBalanceHistoryAdmin(admin.ModelAdmin):
    list_filter = [
         ('balance__asset', admin.RelatedOnlyFieldListFilter),
         ('balance__broker', admin.RelatedOnlyFieldListFilter),
         ('date'),
    ]

    list_display = ('balance', 'round_amount', 'date')

    
    @admin.display(description='Amount')
    def round_amount(self, obj):
        return round(obj.amount, 2)

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_filter = ('type', 'name', 'ticker', 'api_name')
    list_display = ('name', 'ticker_upper', 'api_name', 'type')

    @admin.display(description='Ticker')
    def ticker_upper(self, obj):
        return obj.ticker.upper()

@admin.register(AssetPriceHistory)
class AssetPriceHistoryAdmin(admin.ModelAdmin):
    list_filter = (('asset', admin.RelatedOnlyFieldListFilter), 'date')
    list_display = ('asset', 'date', 'price')

@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    inlines = [ApiConnectionInline]
    list_filter = ('type', )
    list_display = ('name', 'type', 'url')

@admin.register(ApiConnection)
class ApiConnectionAdmin(admin.ModelAdmin):
    list_filter = ('owner', 'broker')
    list_display = ('owner', 'broker')