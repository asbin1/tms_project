from django.db import models
from django.contrib.auth.models import User

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    previous_close = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"

    @property
    def todays_change(self):
        return self.current_price - self.previous_close
    
    @property
    def todays_change_percentage(self):
        if self.previous_close > 0:
            return (self.todays_change / self.previous_close) * 100
        return 0

class Trade(models.Model):
    TRADE_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.trade_type} {self.quantity} {self.stock.symbol}"
    
    @property
    def total_value(self):
        return self.quantity * self.price

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    average_buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'stock']
    
    def __str__(self):
        return f"{self.user.username} - {self.stock.symbol}: {self.quantity}"
    
    @property
    def current_value(self):
        return self.quantity * self.stock.current_price
    
    @property
    def invested_value(self):
        return self.quantity * self.average_buy_price
    
    @property
    def profit_loss(self):
        return self.current_value - self.invested_value
    
    @property
    def profit_loss_percentage(self):
        if self.invested_value > 0:
            return (self.profit_loss / self.invested_value) * 100
        return 0
    
    @property
    def todays_change(self):
        return self.stock.todays_change * self.quantity
    
    @property
    def todays_change_percentage(self):
        return self.stock.todays_change_percentage
        