from django.shortcuts import render
from .models import Portfolio, Asset, AssetBalance, AssetBalanceHistory
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic

def index(request):
    """View function for the home page of the site."""

    portfolio_object = Portfolio.objects.all()[0]

    context = {
        'portfolio_object': portfolio_object,
    }

    return render(request, 'index.html', context=context)


class DashboardView(generic.TemplateView, LoginRequiredMixin):
    """View function for the user dashboard"""

    template_name = 'dashboard.html'

    def get_context_data(self):

        user_portfolio = Portfolio.objects.filter(owner=self.request.user)[0]

        context = {
            'user_portfolio': user_portfolio,
        }
        return context






