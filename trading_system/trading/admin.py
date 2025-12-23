from django.contrib import admin
from .models import Stock, Trade, Portfolio

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'current_price', 'last_updated']
    list_editable = ['current_price']
    search_fields = ['symbol', 'name']
    list_filter = ['last_updated']

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'trade_type', 'quantity', 'price', 'timestamp']
    list_filter = ['trade_type', 'timestamp']
    search_fields = ['user__username', 'stock__symbol']
    date_hierarchy = 'timestamp'

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'stock', 'quantity', 'average_buy_price', 'last_updated']
    search_fields = ['user__username', 'stock__symbol']
    list_filter = ['last_updated']