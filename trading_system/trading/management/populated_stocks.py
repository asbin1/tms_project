import os
import sys
import django

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_system.settings')
django.setup()

from trading.models import Stock

def populate_stocks():
    stocks = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'current_price': 175.00},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'current_price': 135.50},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'current_price': 330.00},
        {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'current_price': 145.00},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'current_price': 230.00},
        {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'current_price': 350.00},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'current_price': 480.00},
        {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'current_price': 550.00},
        {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.', 'current_price': 155.00},
        {'symbol': 'V', 'name': 'Visa Inc.', 'current_price': 250.00},
        {'symbol': 'WMT', 'name': 'Walmart Inc.', 'current_price': 165.00},
        {'symbol': 'MA', 'name': 'Mastercard Inc.', 'current_price': 420.00},
        {'symbol': 'PG', 'name': 'Procter & Gamble', 'current_price': 155.00},
        {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'current_price': 160.00},
        {'symbol': 'DIS', 'name': 'Walt Disney Co.', 'current_price': 90.00},
    ]
    
    for stock_data in stocks:
        stock, created = Stock.objects.get_or_create(
            symbol=stock_data['symbol'],
            defaults={
                'name': stock_data['name'],
                'current_price': stock_data['current_price']
            }
        )
        
        if created:
            print(f'✓ Created stock: {stock.symbol} - {stock.name}')
        else:
            print(f'○ Stock {stock.symbol} already exists')

if __name__ == '__main__':
    print("Populating stocks...")
    populate_stocks()
    print("Done!")