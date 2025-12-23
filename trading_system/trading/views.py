from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Trade, Portfolio, Stock
from .forms import TradeForm

@login_required
def dashboard(request):
    portfolio_items = Portfolio.objects.filter(user=request.user)
    
    total_value = 0
    for item in portfolio_items:
        total_value += item.current_value
    
    context = {
        'portfolio_items': portfolio_items,
        'total_value': total_value,
        'balance': request.user.profile.balance,
    }
    return render(request, 'trading/dashboard.html', context)

@login_required
def trade_view(request):
    if request.method == 'POST':
        form = TradeForm(request.POST)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.user = request.user
            trade.price = trade.stock.current_price
            
            if trade.trade_type == 'BUY':
                total_cost = trade.quantity * trade.price
                if request.user.profile.balance < total_cost:
                    messages.error(request, 'Insufficient balance!')
                    return redirect('trade')
                
                request.user.profile.balance -= total_cost
                request.user.profile.save()
                
                portfolio_item, created = Portfolio.objects.get_or_create(
                    user=request.user,
                    stock=trade.stock,
                    defaults={'quantity': trade.quantity, 'average_buy_price': trade.price}
                )
                
                if not created:
                    total_shares = portfolio_item.quantity + trade.quantity
                    total_cost_existing = portfolio_item.quantity * portfolio_item.average_buy_price
                    total_cost_new = trade.quantity * trade.price
                    new_avg_price = (total_cost_existing + total_cost_new) / total_shares
                    
                    portfolio_item.quantity = total_shares
                    portfolio_item.average_buy_price = new_avg_price
                    portfolio_item.save()
                messages.success(request, f'Successfully bought {trade.quantity} shares of {trade.stock.symbol}')
            
            else:
                try:
                    portfolio_item = Portfolio.objects.get(user=request.user, stock=trade.stock)
                    if portfolio_item.quantity < trade.quantity:
                        messages.error(request, 'Insufficient shares!')
                        return redirect('trade')
                    
                    portfolio_item.quantity -= trade.quantity
                    if portfolio_item.quantity == 0:
                        portfolio_item.delete()
                    else:
                        portfolio_item.save()
                    
                    total_value = trade.quantity * trade.price
                    request.user.profile.balance += total_value
                    request.user.profile.save()
                    messages.success(request, f'Successfully sold {trade.quantity} shares of {trade.stock.symbol}')
                    
                except Portfolio.DoesNotExist:
                    messages.error(request, 'You do not own this stock!')
                    return redirect('trade')
            
            trade.save()
            return redirect('dashboard')
    else:
        form = TradeForm()
    
    stocks = Stock.objects.all()
    
    context = {
        'form': form,
        'stocks': stocks,
    }
    return render(request, 'trading/trade.html', context)

@login_required
def portfolio_view(request):
    portfolio_items = Portfolio.objects.filter(user=request.user)
    
    total_invested = 0
    total_current = 0
    
    for item in portfolio_items:
        item.current_value = item.current_value
        item.invested_value = item.invested_value
        item.profit_loss = item.profit_loss
        item.profit_loss_percentage = item.profit_loss_percentage
        
        total_invested += item.invested_value
        total_current += item.current_value
    
    total_pl = total_current - total_invested
    total_pl_percentage = (total_pl / total_invested * 100) if total_invested > 0 else 0
    
    context = {
        'portfolio_items': portfolio_items,
        'total_invested': total_invested,
        'total_current': total_current,
        'total_pl': total_pl,
        'total_pl_percentage': total_pl_percentage,
    }
    return render(request, 'trading/portfolio.html', context)

@login_required
def analytics_view(request):
    trades = Trade.objects.filter(user=request.user).order_by('-timestamp')[:50]
    portfolio_items = Portfolio.objects.filter(user=request.user)
    
    total_invested = 0
    total_current = 0
    for item in portfolio_items:
        total_invested += item.invested_value
        total_current += item.current_value
    
    profit_loss = total_current - total_invested
    profit_loss_percentage = (profit_loss / total_invested * 100) if total_invested > 0 else 0
    
    context = {
        'trades': trades,
        'total_invested': total_invested,
        'total_current': total_current,
        'profit_loss': profit_loss,
        'profit_loss_percentage': profit_loss_percentage,
        'balance': request.user.profile.balance,
        'total_portfolio_value': total_current + float(request.user.profile.balance),
    }
    return render(request, 'trading/analytics.html', context)