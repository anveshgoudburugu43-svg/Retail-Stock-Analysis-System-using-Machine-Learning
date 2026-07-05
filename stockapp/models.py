from django.db import models

SEASONS = [
    ('Winter', 'Winter'),
    ('Spring', 'Spring'),
    ('Summer', 'Summer'),
    ('Autumn', 'Autumn'),
]

class Stock(models.Model):
    symbol = models.CharField(max_length=10)
    company = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    change = models.FloatField(null=True, blank=True)
    quantity = models.IntegerField()
    revenue_ttm = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    same_store_sales = models.CharField(max_length=50, null=True, blank=True)
    season = models.CharField(max_length=10, choices=SEASONS, null=True, blank=True)
    recommendation = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)

    @property
    def low_stock(self):
        return self.quantity < 10

    def __str__(self):
        return f"{self.symbol} - {self.company}"


class Sale(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField()
    quantity_sold = models.IntegerField()
    revenue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Automatically calculate revenue based on quantity sold and stock price
        if self.stock and self.quantity_sold:
            self.revenue = self.quantity_sold * self.stock.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.stock.symbol} - {self.date}"
