from django.contrib import admin
from .models import Portfolio, Cash, CashHistory, Stock, StockHistory, Crypto, CryptoHistory
# Register your models here.

admin.site.register(Stock)
admin.site.register(StockHistory)
admin.site.register(Crypto)
admin.site.register(CryptoHistory)

# Defining inlines
class CashInline(admin.TabularInline):
    model = Cash
    extra = 1

class StockInline(admin.TabularInline):
    model = Stock
    extra = 1

class CryptoInline(admin.TabularInline):
    model = Crypto
    extra = 1

class CashHistoryInline(admin.TabularInline):
    model = CashHistory
    
# Admin models
@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    inlines = [CashInline, StockInline, CryptoInline]

@admin.register(Cash)
class CashAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'currency')
    inlines = [CashHistoryInline]

@admin.register(CashHistory)
class CashHistoryAdmin(admin.ModelAdmin):
    list_display = ('cash', 'amount', 'date')
    list_filter = ('cash',)


