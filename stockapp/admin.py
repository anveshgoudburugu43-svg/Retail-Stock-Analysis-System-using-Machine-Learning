from django.contrib import admin
from django.utils.html import format_html
from .models import Stock

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'company', 'price', 'quantity_colored', 'change_colored', 'updated')
    search_fields = ('symbol', 'company')
    list_filter = ('updated',)
    date_hierarchy = 'updated'

    def quantity_colored(self, obj):
        color = 'red' if obj.quantity < 10 else 'green'
        return format_html('<span style="color: {};">{}</span>', color, obj.quantity)
    quantity_colored.short_description = 'Quantity'

    def change_colored(self, obj):
        color = 'green' if obj.change >= 0 else 'red'
        return format_html('<span style="color: {};">{}</span>', color, obj.change)
    change_colored.short_description = 'Change'
