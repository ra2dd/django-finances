from django.shortcuts import render
from .models import Portfolio, Cash, CashHistory, Stock, StockHistory, Crypto, CryptoHistory

def index(request):
    """View function for the home page of the site."""

    portfolio_object = Portfolio.objects.all()[0]

    context = {
        'portfolio_object': portfolio_object,
    }

    return render(request, 'index.html', context=context)

