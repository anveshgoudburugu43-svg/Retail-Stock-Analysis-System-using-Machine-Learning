import random
from datetime import timedelta, date
from stockapp.models import Stock, Sale

# Clear old data
Sale.objects.all().delete()

stocks = Stock.objects.all()
today = date.today()

# Create random sales for the last 20 days
for stock in stocks:
    for i in range(20):
        sale_date = today - timedelta(days=i)
        quantity_sold = random.randint(0, 10)

        if quantity_sold > 0:
            Sale.objects.create(
                stock=stock,
                date=sale_date,
                quantity_sold=quantity_sold
            )

print("✅ Added random sales data for all stocks!")
