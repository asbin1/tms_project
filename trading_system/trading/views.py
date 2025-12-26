from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count, Avg
from decimal import Decimal
import json
from datetime import datetime, timedelta
import random

from .models import Stock, Trade, Portfolio
from .forms import TradeForm

# Helper Functions
def validate_trade(user, stock, trade_type, quantity, price):
    """Validate if a trade can be executed"""
    total_cost = Decimal(str(quantity)) * Decimal(str(price))
    
    if trade_type == 'BUY':
        if user.profile.balance < total_cost:
            return False, f'Insufficient balance! Need Rs.{total_cost:.2f}, have Rs.{user.profile.balance:.2f}'
    elif trade_type == 'SELL':
        try:
            portfolio_item = Portfolio.objects.get(user=user, stock=stock)
            if portfolio_item.quantity < quantity:
                return False, f'Insufficient shares! Have {portfolio_item.quantity}, trying to sell {quantity}'
        except Portfolio.DoesNotExist:
            return False, 'You do not own this stock'
            
    return True, None

def execute_trade_logic(user, stock, trade_type, quantity, price):
    """Execute the trade logic (Update balance, portfolio, create record)"""
    try:
        total_value = Decimal(str(quantity)) * Decimal(str(price))
        profit_loss = Decimal('0.00')
        
        if trade_type == 'BUY':
            # Double check validation to be safe
            if user.profile.balance < total_value:
                return False, "Insufficient balance", None

            # Update balance
            user.profile.balance -= total_value
            user.profile.save()
            
            # Update Portfolio
            portfolio_item, created = Portfolio.objects.get_or_create(
                user=user,
                stock=stock,
                defaults={'quantity': 0, 'average_buy_price': 0}
            )
            
            # Calculate new average price
            current_total_value = portfolio_item.quantity * portfolio_item.average_buy_price
            new_total_value = current_total_value + total_value
            new_quantity = portfolio_item.quantity + quantity
            
            if new_quantity > 0:
                new_avg_price = new_total_value / new_quantity
            else:
                new_avg_price = price # Should not happen for buy
                
            portfolio_item.quantity = new_quantity
            portfolio_item.average_buy_price = new_avg_price
            portfolio_item.save()
            
            message = f"Bought {quantity} shares of {stock.symbol} at Rs.{price:.2f}"
            
        else: # SELL
            portfolio_item = Portfolio.objects.get(user=user, stock=stock)
            if portfolio_item.quantity < quantity:
                return False, "Insufficient shares", None
                
            # Calculate profit/loss
            profit_loss = (Decimal(str(price)) - portfolio_item.average_buy_price) * quantity
            
            # Update Portfolio
            portfolio_item.quantity -= quantity
            if portfolio_item.quantity == 0:
                portfolio_item.delete()
            else:
                portfolio_item.save()
                
            # Update Balance
            user.profile.balance += total_value
            user.profile.save()
            
            pl_text = "profit" if profit_loss >= 0 else "loss"
            message = f"Sold {quantity} shares of {stock.symbol} at Rs.{price:.2f} (Rs.{abs(profit_loss):.2f} {pl_text})"

        # Create Trade Record
        trade = Trade.objects.create(
            user=user,
            stock=stock,
            trade_type=trade_type,
            quantity=quantity,
            price=price
        )
        
        return True, message, {'trade': trade, 'profit_loss': profit_loss}

    except Exception as e:
        return False, str(e), None


@login_required
def dashboard(request):
    """Enhanced dashboard with portfolio overview"""
    # Get user's portfolio
    portfolio_items = Portfolio.objects.filter(user=request.user).select_related('stock')
    
    # Calculate portfolio statistics
    total_invested = Decimal('0.00')
    total_current = Decimal('0.00')
    total_profit_loss = Decimal('0.00')
    todays_pl = Decimal('0.00')
    
    for item in portfolio_items:
        # We access properties directly instead of assigning them
        total_invested += item.invested_value
        total_current += item.current_value
        total_profit_loss += item.profit_loss
        todays_pl += item.todays_change
    
    # Get recent trades
    recent_trades = Trade.objects.filter(user=request.user).order_by('-timestamp')[:5]
    
    # Get all stocks for quick trade
    all_stocks = Stock.objects.all()[:10]
    
    # Get market news
    market_news = [
        {'title': 'NEPSE Index crosses 2500 points', 'time': '2 min ago', 'impact': 'positive'},
        {'title': 'NRB announces new monetary policy review', 'time': '1 hour ago', 'impact': 'neutral'},
        {'title': 'Hydropower sector gains momentum', 'time': '2 hours ago', 'impact': 'positive'},
        {'title': 'SEBON approves new IPOs', 'time': '4 hours ago', 'impact': 'positive'},
    ]
    
    # Get watchlist
    watchlist_stocks = Stock.objects.filter(
        Q(symbol__in=[item.stock.symbol for item in portfolio_items]) | 
        Q(symbol__in=['NABIL', 'NTC', 'HDL', 'NICA', 'SHPC'])
    ).distinct()[:8]
    
    context = {
        'portfolio_items': portfolio_items,
        'total_invested': total_invested,
        'total_current': total_current,
        'total_profit_loss': total_profit_loss,
        'total_profit_loss_percentage': (total_profit_loss / total_invested * 100) if total_invested > 0 else Decimal('0.00'),
        'todays_pl': todays_pl,
        'balance': request.user.profile.balance,
        'recent_trades': recent_trades,
        'market_news': market_news,
        'watchlist_stocks': watchlist_stocks,
        'all_stocks': all_stocks,
    }
    return render(request, 'trading/dashboard.html', context)

@login_required
def trade_view(request):
    """Trade page with buy/sell functionality"""
    if request.method == 'POST':
        form = TradeForm(request.POST)
        if form.is_valid():
            # Don't save yet, we need to execute logic
            trade_data = form.cleaned_data
            stock = trade_data['stock']
            trade_type = trade_data['trade_type']
            quantity = trade_data['quantity']
            price = stock.current_price # Use current price
            
            # Validate
            is_valid, error_msg = validate_trade(request.user, stock, trade_type, quantity, price)
            if not is_valid:
                messages.error(request, error_msg)
                return redirect('trade')
            
            # Execute
            success, message, result = execute_trade_logic(request.user, stock, trade_type, quantity, price)
            
            if success:
                messages.success(request, message)
                return redirect('dashboard')
            else:
                messages.error(request, f"Trade failed: {message}")
                return redirect('trade')
    else:
        initial_stock = request.GET.get('stock')
        if initial_stock:
            try:
                stock_obj = Stock.objects.get(symbol=initial_stock)
                form = TradeForm(initial={'stock': stock_obj})
            except Stock.DoesNotExist:
                form = TradeForm()
        else:
            form = TradeForm()
    
    stocks = Stock.objects.all()
    user_portfolio = Portfolio.objects.filter(user=request.user).select_related('stock')
    
    context = {
        'form': form,
        'stocks': stocks,
        'user_portfolio': user_portfolio,
        'balance': request.user.profile.balance,
    }
    return render(request, 'trading/trade.html', context)

@login_required
def portfolio_view(request):
    """Portfolio management page"""
    portfolio_items = Portfolio.objects.filter(user=request.user).select_related('stock')
    
    # Calculate totals
    total_invested = Decimal('0.00')
    total_current = Decimal('0.00')
    todays_pl = Decimal('0.00')
    
    for item in portfolio_items:
        # Access properties directly
        total_invested += item.invested_value
        total_current += item.current_value
        todays_pl += item.todays_change
    
    total_pl = total_current - total_invested
    total_pl_percentage = (total_pl / total_invested * 100) if total_invested > 0 else 0
    
    # Get trade history
    trades = Trade.objects.filter(user=request.user).order_by('-timestamp')[:10]
    
    # Simulated sector allocation
    sectors = {
        'Banking': random.randint(30, 45),
        'Hydropower': random.randint(20, 35),
        'Life Insurance': random.randint(10, 20),
        'Microfinance': random.randint(5, 10),
        'Investment': random.randint(5, 10),
        'Others': random.randint(5, 10),
    }
    
    context = {
        'portfolio_items': portfolio_items,
        'total_invested': total_invested,
        'total_current': total_current,
        'total_pl': total_pl,
        'total_pl_percentage': total_pl_percentage,
        'todays_pl': todays_pl,
        'trades': trades,
        'sectors': sectors,
        'balance': request.user.profile.balance,
    }
    return render(request, 'trading/portfolio.html', context)

@login_required
def analytics_view(request):
    """Trading analytics page"""
    # Get all trades
    trades = Trade.objects.filter(user=request.user).order_by('-timestamp')
    
    # Calculate basic stats
    total_trades = trades.count()
    buy_trades = trades.filter(trade_type='BUY').count()
    sell_trades = trades.filter(trade_type='SELL').count()
    
    # Calculate profit/loss from sells
    profitable_trades = 0
    total_profit = Decimal('0.00')
    
    for trade in trades.filter(trade_type='SELL'):
        try:
            # Find corresponding buy (simplified)
            buy_trade = Trade.objects.filter(
                user=request.user,
                stock=trade.stock,
                trade_type='BUY',
                timestamp__lt=trade.timestamp
            ).order_by('-timestamp').first()
            
            if buy_trade:
                profit = (trade.price - buy_trade.price) * trade.quantity
                total_profit += profit
                if profit > 0:
                    profitable_trades += 1
        except:
            pass
    
    win_rate = (profitable_trades / sell_trades * 100) if sell_trades > 0 else 0
    
    # Portfolio performance
    portfolio_items = Portfolio.objects.filter(user=request.user)
    total_invested = sum(item.quantity * item.average_buy_price for item in portfolio_items)
    total_current = sum(item.quantity * item.stock.current_price for item in portfolio_items)
    portfolio_return = total_current - total_invested
    portfolio_return_percentage = (portfolio_return / total_invested * 100) if total_invested > 0 else 0
    
    # Monthly performance (simulated)
    months = []
    for i in range(6, -1, -1):
        month_date = datetime.now() - timedelta(days=30*i)
        month_name = month_date.strftime('%b')
        performance = random.randint(-10, 20)
        months.append({
            'month': month_name,
            'performance': performance,
            'color': 'success' if performance > 0 else 'danger'
        })
    
    # Most traded stocks
    most_traded = trades.values('stock__symbol').annotate(
        count=Count('id'),
        total_volume=Sum('quantity')
    ).order_by('-count')[:5]
    
    context = {
        'trades': trades[:20],
        'total_trades': total_trades,
        'buy_trades': buy_trades,
        'sell_trades': sell_trades,
        'win_rate': win_rate,
        'total_profit': total_profit,
        'profit_loss': portfolio_return,
        'profit_loss_percentage': portfolio_return_percentage,
        'total_portfolio_value': total_current + request.user.profile.balance,
        'months': months,
        'most_traded': most_traded,
        'balance': request.user.profile.balance,
    }
    return render(request, 'trading/analytics.html', context)

@login_required
def quick_trade(request):
    """Handle quick trades via AJAX"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            stock_id = data.get('stock_id')
            trade_type = data.get('trade_type')
            quantity = int(data.get('quantity', 1))
            
            stock = get_object_or_404(Stock, id=stock_id)
            price = stock.current_price
            
            # Validate
            is_valid, error_msg = validate_trade(request.user, stock, trade_type, quantity, price)
            if not is_valid:
                return JsonResponse({'success': False, 'error': error_msg})
            
            # Execute
            success, message, result = execute_trade_logic(request.user, stock, trade_type, quantity, price)
            
            if success:
                response_data = {
                    'success': True,
                    'message': message,
                    'new_balance': float(request.user.profile.balance),
                }
                if 'profit_loss' in result:
                    response_data['profit_loss'] = float(result['profit_loss'])
                
                return JsonResponse(response_data)
            else:
                 return JsonResponse({'success': False, 'error': message})
                    
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})