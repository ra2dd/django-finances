from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password

from ..models import Exchange, ApiConnection, AssetPriceHistory, Asset, AssetBalance, AssetBalanceHistory
from ..tasks import client_tasks, server_tasks
from ..forms import ConnectionAddModelForm

def fetch_exchange(self):
    return Exchange.objects.filter(pk=self.kwargs['pk'])[0]


class ExchangeListView(generic.ListView, LoginRequiredMixin):
    """View function for listing exchanges and their user wallet connections"""

    template_name = 'connections/exchange_list.html'
    model = Exchange

    def get_context_data(self, **kwargs):
        
        '''
        connection = ApiConnection.objects.filter(owner=self.request.user).filter(broker=Exchange.objects.filter(name='Binance')[0])[0] 
        api_key = connection.api_key
        secret_key = connection.secret_key

        #client_tasks.import_binance_balance(api_key, secret_key)
        client_tasks.import_binance_balance(api_key, secret_key)
        '''
        # server_tasks.get_crypto_assets()
        asset_test = Asset.objects.filter(api_name='bitcoin')[0]
        
        context = super().get_context_data(**kwargs)
        context['asset_test'] = asset_test
        return context


class ExchangeDetailView(generic.DetailView, LoginRequiredMixin):
    """View function for displaying exchange details and its user connection info"""
    model = Exchange
    template_name = 'connections/exchange_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        api_connection = ApiConnection.objects.filter(broker=fetch_exchange(self)).filter(owner=self.request.user)
        api_connection_exists = None
        if len(api_connection) == 0:
            api_connection_exists = False
        else:
            api_connection_exists = True

        context["api_connection_exists"] = api_connection_exists

        return context


class ApiConnectionAdd(generic.CreateView, LoginRequiredMixin):
    """View function for adding user ApiConnection to exchange"""

    model = ApiConnection
    form_class = ConnectionAddModelForm
    template_name = 'connections/apiconnection_add.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['exchange_object'] = fetch_exchange(self)
        kwargs["user_object"] = self.request.user

        return kwargs
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.broker = fetch_exchange(self)
        self.object.owner = self.request.user
        # self.object.api_key = make_password(self.object.api_key)
        # self.object.secret_key = make_password(self.object.secret_key)
        self.object.save()

        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.broker.get_absolute_url()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exchange"] = fetch_exchange(self)

        return context

    # TODO: disable autocomplete in forms


class ApiConnectionDelete(generic.DeleteView, LoginRequiredMixin):
    model = ApiConnection
    template_name = 'connections/apiconnection_delete.html'

    def get_success_url(self):
        return self.object.broker.get_absolute_url()
        # return reverse_lazy('exchange-detail', args=str(self.kwargs['pk']))

    def get_object(self):
        object = ApiConnection.objects.filter(broker=fetch_exchange(self)).filter(owner=self.request.user)[0]
        return object
    
    def form_valid(self, form):

        related_balance = AssetBalance.objects.filter(portfolio=self.request.user.portfolio).filter(broker=self.object.broker)

        for balance in related_balance:
            related_balance_history = AssetBalanceHistory.objects.filter(balance=balance)

            for balance_history in related_balance_history:
                balance_history.delete()

            balance.delete()

        return super().form_valid(self)


@require_http_methods(["GET"])
@login_required
def fetch_apiconnection_balance_view(request, pk):

    if request.method == 'GET':
        exchange = Exchange.objects.filter(pk=pk)[0]
        api_connection = ApiConnection.objects.filter(broker=exchange).filter(owner=request.user)

        if(len(api_connection) == 0):
            raise Http404("Connot update connection data.")
  
        elif(len(api_connection) > 1):
            raise Http404("Connot update connection data, too many api connections.")
  
        elif(len(api_connection) == 1):
            client_tasks.import_balance(exchange, api_connection[0], request.user)    
        
        return HttpResponseRedirect(reverse('exchange-detail', args=str(pk)))
