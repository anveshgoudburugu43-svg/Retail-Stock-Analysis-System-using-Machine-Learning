import random
from datetime import date, timedelta
from stockapp.models import Stock, Sale

# Clear old sales if needed
Sale.objects.all().delete()

# Create random sales for each stock for the last 20 days
stocks = Stock.objects.all()
today = date.today()

for stock in stocks:
    for i in range(20):  # last 20 days
        sale_date = today - timedelta(days=i)
        quantity_sold = random.randint(0, 10)
        if quantity_sold > 0:
            Sale.objects.create(
                stock=stock,
                date=sale_date,
                quantity_sold=quantity_sold
            )

print("✅ Added random sales data for all stocks!")
