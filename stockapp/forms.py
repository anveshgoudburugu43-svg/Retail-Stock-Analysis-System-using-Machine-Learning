from django import forms
from .models import Stock, Sale
from datetime import date

# ================================
# Stock Form
# ================================
class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            'symbol', 'company', 'price', 'change', 
            'quantity', 'category', 'revenue_ttm', 'same_store_sales'
        ]
        widgets = {
            'symbol': forms.TextInput(attrs={'class':'border p-2 rounded w-full', 'placeholder':'Stock symbol'}),
            'company': forms.TextInput(attrs={'class':'border p-2 rounded w-full', 'placeholder':'Company name'}),
            'price': forms.NumberInput(attrs={'class':'border p-2 rounded w-full', 'placeholder':'Price in ₹'}),
            'change': forms.NumberInput(attrs={'class':'border p-2 rounded w-full', 'placeholder':'% Change'}),
            'quantity': forms.NumberInput(attrs={'class':'border p-2 rounded w-full', 'placeholder':'Available quantity'}),
            'category': forms.TextInput(attrs={'class':'border p-2 rounded w-full', 'placeholder':'Category'}),
            'revenue_ttm': forms.NumberInput(attrs={'class':'border p-2 rounded w-full', 'placeholder':'Revenue TTM'}),
            'same_store_sales': forms.TextInput(attrs={'class':'border p-2 rounded w-full', 'placeholder':'Same store sales'}),
        }

    def clean_symbol(self):
        symbol = self.cleaned_data.get('symbol').upper()
        if not symbol.isalnum():
            raise forms.ValidationError("Symbol must be alphanumeric.")
        return symbol

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        return quantity

    def clean_change(self):
        change = self.cleaned_data.get('change')
        if change is None:
            return 0
        return change

# ================================
# Sale Form
# ================================
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['stock', 'date', 'quantity_sold', 'revenue']
        widgets = {
            'stock': forms.Select(attrs={'class': 'border p-2 rounded w-full'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'border p-2 rounded w-full', 'value': date.today()}),
            'quantity_sold': forms.NumberInput(attrs={'class': 'border p-2 rounded w-full', 'placeholder':'Quantity sold'}),
            'revenue': forms.NumberInput(attrs={'class': 'border p-2 rounded w-full', 'placeholder':'Revenue generated'}),
        }

    def clean_quantity_sold(self):
        qty = self.cleaned_data.get('quantity_sold')
        if qty <= 0:
            raise forms.ValidationError("Quantity sold must be greater than zero.")
        return qty

    def clean_revenue(self):
        rev = self.cleaned_data.get('revenue')
        if rev < 0:
            raise forms.ValidationError("Revenue cannot be negative.")
        return rev
