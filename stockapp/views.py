from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F, Min, Max
from django.http import HttpResponse
from datetime import date, timedelta

import csv
import json

from .models import Stock, Sale
from .forms import StockForm

# ================================
# CSV Export
# ================================
def export_sales(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_summary.csv"'

    writer = csv.writer(response)
    writer.writerow(['Product Symbol', 'Company', 'Category', 'Price', 'Total Sold', 'Current Stock'])

    stocks = Stock.objects.all()
    for stock in stocks:
        total_sold = Sale.objects.filter(stock=stock).aggregate(total=Sum('quantity_sold'))['total'] or 0
        writer.writerow([
            stock.symbol,
            stock.company,
            stock.category,
            stock.price,
            total_sold,
            stock.quantity
        ])
    return response

# ================================
# Landing Page
# ================================
def about(request):
    return render(request, 'about.html', {'now': now()})

@login_required
def sale_view(request):
    stocks = Stock.objects.all()
    if request.method == 'POST':
        stock_id = request.POST.get('stock_id')
        quantity_sold = int(request.POST.get('quantity_sold', 0))
        stock = get_object_or_404(Stock, id=stock_id)

        if quantity_sold <= 0:
            messages.error(request, "Enter a valid quantity.")
        elif quantity_sold > stock.quantity:
            messages.error(request, f"Cannot sell more than {stock.quantity} available.")
        else:
            Sale.objects.create(stock=stock, date=date.today(), quantity_sold=quantity_sold)
            stock.quantity -= quantity_sold
            stock.save()
            messages.success(request, f"Sale recorded for {stock.symbol}.")
            return redirect('home')

    return render(request, 'sale.html', {'stocks': stocks})

def custom_logout(request):
    logout(request)
    messages.success(request, "✅ You have successfully logged out.")
    return redirect('about')

# ================================
# Authentication
# ================================
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            messages.error(request, "Username and password are required.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')
    return render(request, 'signup.html')

def signin_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Welcome back!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password!")
    return render(request, 'signin.html')

@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('signin')

# ================================
# Seasons & Festivals
# ================================
SEASONS = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Autumn", 10: "Autumn", 11: "Autumn"
}

FESTIVALS = [
    {"name": "Diwali", "month": 11, "days": [5, 6, 7, 8, 9, 10]},
    {"name": "Christmas", "month": 12, "days": [20, 21, 22, 23, 24, 25]},
    {"name": "Pongal", "month": 1, "days": [13, 14, 15]},
    {"name": "Eid", "month": 4, "days": [9, 10, 11]},
]

def get_season(month):
    return SEASONS.get(month, "Unknown")

def get_upcoming_festival(today: date):
    upcoming = None
    min_diff = 365
    for fest in FESTIVALS:
        for day in fest["days"]:
            fest_date = date(today.year, fest["month"], day)
            diff = (fest_date - today).days
            if diff >= 0 and diff < min_diff:
                min_diff = diff
                upcoming = {"name": fest["name"], "days_left": diff}
    return upcoming

@login_required
def restock_recommendations(request):
    stocks = Stock.objects.all()
    product_data = []

    for stock in stocks:
        sales = Sale.objects.filter(stock=stock)
        total_sold = sales.aggregate(total=Sum('quantity_sold'))['total'] or 0
        first_sale = sales.aggregate(first=Min('date'))['first']
        last_sale = sales.aggregate(last=Max('date'))['last']

        if first_sale and last_sale:
            days_selling = (last_sale - first_sale).days + 1
            avg_daily_sales = total_sold / days_selling if days_selling > 0 else total_sold
        else:
            avg_daily_sales = 0

        recommended_stock = round(avg_daily_sales * 7)
        product_data.append({
            'symbol': stock.symbol,
            'company': stock.company,
            'category': stock.category,
            'price': stock.price,
            'stock_left': stock.quantity,
            'avg_daily_sales': round(avg_daily_sales, 2),
            'recommended_stock': recommended_stock,
            'low_stock': stock.quantity < recommended_stock
        })

    # Pagination
    paginator = Paginator(product_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'restock.html', {'page_obj': page_obj})

# ================================
# Home Page
# ================================
@login_required
def home(request):
    # ===== Filters =====
    selected_category = request.GET.get('category', 'All')
    search = request.GET.get('search', '')

    stocks = Stock.objects.all()
    if selected_category != 'All':
        stocks = stocks.filter(category=selected_category)
    if search:
        stocks = stocks.filter(Q(symbol__icontains=search) | Q(company__icontains=search))

    # ===== Stock Table Pagination =====
    paginator = Paginator(stocks.order_by('id'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ===== Stats =====
    total_products = stocks.count()
    low_stock_count = stocks.filter(quantity__lt=10).count()
    last_updated = stocks.order_by('-updated').first().updated if stocks.exists() else None

    # ===== Charts Data (Last 20 Days) =====
    today_date = date.today()
    last_20_days = today_date - timedelta(days=19)

    recent_sales_qs = (
        Sale.objects.filter(date__gte=last_20_days)
        .annotate(calc_revenue=F('quantity_sold') * F('stock__price'))
        .values('date')
        .annotate(total_revenue=Sum('calc_revenue'))
        .order_by('date')
    )
    sales_dates = [s['date'].strftime('%Y-%m-%d') for s in recent_sales_qs] if recent_sales_qs.exists() else []
    sales_revenue = [float(s['total_revenue']) for s in recent_sales_qs] if recent_sales_qs.exists() else []

    top_selling_qs = (
        Sale.objects.values('stock__symbol')
        .annotate(total_sold=Sum('quantity_sold'))
        .order_by('-total_sold')[:5]
    )
    top_labels = [s['stock__symbol'] for s in top_selling_qs] if top_selling_qs.exists() else []
    top_values = [s['total_sold'] for s in top_selling_qs] if top_selling_qs.exists() else []

    low_stock_qs = stocks.filter(quantity__lt=20).values('symbol', 'quantity')
    low_labels = [s['symbol'] for s in low_stock_qs] if low_stock_qs.exists() else []
    low_qty = [s['quantity'] for s in low_stock_qs] if low_stock_qs.exists() else []

    low_stock_items = stocks.filter(quantity__lt=10)

    # ===== Restock Recommendations =====
    product_data = []
    for stock in stocks:
        sales = Sale.objects.filter(stock=stock)
        total_sold = sales.aggregate(total=Sum('quantity_sold'))['total'] or 0
        first_sale = sales.aggregate(first=Min('date'))['first']
        last_sale = sales.aggregate(last=Max('date'))['last']

        if first_sale and last_sale:
            days_selling = (last_sale - first_sale).days + 1
            avg_daily_sales = total_sold / days_selling if days_selling > 0 else total_sold
        else:
            avg_daily_sales = 0

        recommended_stock = round(avg_daily_sales * 7)
        product_data.append({
            'symbol': stock.symbol,
            'company': stock.company,
            'category': stock.category,
            'price': stock.price,
            'stock_left': stock.quantity,
            'avg_daily_sales': round(avg_daily_sales, 2),
            'recommended_stock': recommended_stock,
            'low_stock': stock.quantity < recommended_stock
        })

    # ===== Restock Pagination =====
    restock_paginator = Paginator(product_data, 7)  # 7 items per page
    restock_page_number = request.GET.get('restock_page')
    restock_page_obj = restock_paginator.get_page(restock_page_number)

    # ===== Context =====
    context = {
        'page_obj': page_obj,
        'restock_page_obj': restock_page_obj,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'last_updated': last_updated,
        'sales_dates': sales_dates,
        'sales_revenue': sales_revenue,
        'top_labels': top_labels,
        'top_values': top_values,
        'low_labels': low_labels,
        'low_qty': low_qty,
        'selected_category': selected_category,
        'categories': Stock.objects.values('category').distinct(),
        'search': search,
        'low_stock_items': low_stock_items,
    }

    return render(request, 'home.html', context)



# ================================
# Stock CRUD
# ================================
@login_required
def add_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock added successfully!")
            return redirect('home')
    else:
        form = StockForm()
    return render(request, 'add.html', {'form': form})

@login_required
def edit_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock updated successfully!")
            return redirect('home')
    else:
        form = StockForm(instance=stock)
    return render(request, 'add.html', {'form': form, 'edit': True})

@login_required
def delete_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    stock.delete()
    messages.success(request, "Stock deleted successfully!")
    return redirect('home')

# ================================
# Sales Management
# ================================
@login_required
def add_sale(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == 'POST':
        quantity_sold = int(request.POST.get('quantity_sold', 0))
        if quantity_sold > stock.quantity:
            messages.error(request, "Cannot sell more than available stock.")
        else:
            Sale.objects.create(stock=stock, date=date.today(), quantity_sold=quantity_sold)
            stock.quantity -= quantity_sold
            stock.save()
            messages.success(request, f"Sale recorded for {stock.symbol}.")
            return redirect('home')
    return render(request, 'add_sale.html', {'stock': stock})

@login_required
def sales_overview(request):
    sales_data = Sale.objects.values('stock__id', 'stock__symbol', 'stock__company') \
                             .annotate(total_sold=Sum('quantity_sold')) \
                             .order_by('-total_sold')
    return render(request, 'sales.html', {'sales_data': sales_data})
