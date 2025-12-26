import os
import django
import random
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_system.settings')
django.setup()

from trading.models import Stock

def populate_nepse():
    nepse_stocks = [
        # Commercial Banks
        ('NABIL', 'Nabil Bank Ltd.', 1250.00),
        ('NICA', 'NIC Asia Bank Ltd.', 780.50),
        ('EBL', 'Everest Bank Ltd.', 540.00),
        ('SCB', 'Standard Chartered Bank Nepal', 515.00),
        ('GIME', 'Global IME Bank Ltd.', 198.00),
        ('NBL', 'Nepal Bank Ltd.', 245.00),
        
        # Development Banks
        ('MNBBL', 'Muktinath Bikas Bank Ltd.', 340.00),
        ('GBBL', 'Garima Bikas Bank Ltd.', 310.00),
        
        # Hydropower
        ('HIDCL', 'Hydroelectricity Investment & Dev. Co.', 185.00),
        ('CHCL', 'Chilime Hydropower Company', 450.00),
        ('API', 'Api Power Company Ltd.', 160.00),
        ('UPPER', 'Upper Tamakoshi Hydropower', 210.00),
        ('SHPC', 'Sanima Mai Hydropower', 320.00),
        
        # Life Insurance
        ('NLIC', 'Nepal Life Insurance Co. Ltd.', 650.00),
        ('LICN', 'Life Insurance Co. Nepal', 1100.00),
        ('ALICL', 'Asian Life Insurance Co.', 580.00),
        
        # Non-Life Insurance
        ('NIL', 'Neco Insurance Ltd.', 820.00),
        ('SICL', 'Shikhar Insurance Co. Ltd.', 890.00),
        
        # Others
        ('NTC', 'Nepal Telecom', 880.00),
        ('CIT', 'Citizen Investment Trust', 2200.00),
        ('HDL', 'Himalayan Distillery Ltd.', 1450.00),
        ('STC', 'Salt Trading Corporation', 4500.00),
        ('UNL', 'Unilever Nepal Ltd.', 38000.00),
    ]

    print("Populating NEPSE Stocks...")
    
    # Optional: Clear existing non-Nepali stocks if you want a clean slate
    # Stock.objects.all().delete() 
    
    count = 0
    for symbol, name, price in nepse_stocks:
        # Simulate a previous close as a baseline for daily changes
        # Use a consistent seeded random or just a slight variation
        prev_close_price = Decimal(str(price)) * Decimal(str(random.uniform(0.98, 1.02)))
        
        stock, created = Stock.objects.get_or_create(
            symbol=symbol,
            defaults={
                'name': name,
                'current_price': Decimal(str(price)),
                'previous_close': prev_close_price
            }
        )
        if created:
            print(f"Created {symbol}")
            count += 1
        else:
            # Update price just in case
            stock.name = name
            stock.current_price = Decimal(str(price))
            if stock.previous_close == 0:
                stock.previous_close = prev_close_price
            stock.save()
            print(f"Updated {symbol}")

    print(f"Done! Added/Updated {len(nepse_stocks)} stocks.")

if __name__ == "__main__":
    populate_nepse()
