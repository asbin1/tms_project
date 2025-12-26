from django.test import TestCase, Client
from django.contrib.auth.models import User
from trading.models import Stock, Portfolio, Trade
from decimal import Decimal
from django.urls import reverse
import json

class TradingLogicTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        # Profile is usually created via signals, ensure it has balance
        self.user.profile.balance = Decimal('10000.00')
        self.user.profile.save()
        
        self.stock = Stock.objects.create(
            symbol='NABIL',
            name='Nabil Bank',
            current_price=Decimal('1000.00'),
            previous_close=Decimal('950.00')
        )
        
        self.client = Client()
        self.client.login(username='testuser', password='password123')

    def test_stock_properties(self):
        self.assertEqual(self.stock.todays_change, Decimal('50.00'))
        self.assertAlmostEqual(self.stock.todays_change_percentage, 5.263157, places=4)

    def test_portfolio_properties(self):
        portfolio = Portfolio.objects.create(
            user=self.user,
            stock=self.stock,
            quantity=10,
            average_buy_price=Decimal('900.00')
        )
        self.assertEqual(portfolio.invested_value, Decimal('9000.00'))
        self.assertEqual(portfolio.current_value, Decimal('10000.00'))
        self.assertEqual(portfolio.profit_loss, Decimal('1000.00'))
        self.assertEqual(portfolio.todays_change, Decimal('500.00'))

    def test_dashboard_view(self):
        Portfolio.objects.create(
            user=self.user,
            stock=self.stock,
            quantity=10,
            average_buy_price=Decimal('900.00')
        )
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['todays_pl'], Decimal('500.00'))

    def test_quick_trade_response(self):
        url = reverse('quick_trade')
        data = {
            'stock_id': self.stock.id,
            'trade_type': 'BUY',
            'quantity': 1
        }
        response = self.client.post(
            url, 
            data=json.dumps(data), 
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        resp_json = response.json()
        self.assertTrue(resp_json['success'])
        self.assertIn('new_balance', resp_json)
        self.assertEqual(resp_json['new_balance'], 9000.0)

    def test_trade_view_prefill(self):
        url = reverse('trade') + '?stock=NABIL'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check if form has initial data
        self.assertEqual(response.context['form'].initial.get('stock'), self.stock)
