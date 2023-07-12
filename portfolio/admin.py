from django.contrib import admin
from .models import Portfolio, Cash, CashHistory, Stock, StockHistory, Crypto, CryptoHistory
# Register your models here.

admin.site.register(Portfolio)
# admin.site.register(Cash)
# admin.site.register(CashHistory)
admin.site.register(Stock)
admin.site.register(StockHistory)
admin.site.register(Crypto)
admin.site.register(CryptoHistory)

class CashAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'currency')

admin.site.register(Cash, CashAdmin)

class CashHistoryAdmin(admin.ModelAdmin):
    list_display = ('cash', 'amount', 'date')

admin.site.register(CashHistory, CashHistoryAdmin)


