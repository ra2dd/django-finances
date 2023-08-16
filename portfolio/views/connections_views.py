from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password

from ..models import Exchange, ApiConnection, AssetPriceHistory, Asset
from ..tasks import client_tasks, server_tasks
from ..forms import AddConnectionModelForm

def fetch_exchange(self):
    return Exchange.objects.filter(pk=self.kwargs['pk'])[0]

class ConnectionsView(generic.ListView, LoginRequiredMixin):
    """View function for listing user wallet connections"""

    template_name = 'connections/connections_list.html'
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


class ConnectionInfoView(generic.DetailView, LoginRequiredMixin):
    """View function for displaying connection info"""
    model = Exchange
    template_name = 'connections/connection_detail.html'

class AddConnectionModelForm(generic.CreateView, LoginRequiredMixin):
    """View function for connecting user exchange data"""

    model = ApiConnection
    form_class = AddConnectionModelForm
    template_name = 'connections/connection_add.html'

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
        return reverse('connection-detail', args=[str(self.kwargs['pk'])])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exchange"] = fetch_exchange(self)

        return context

    # TODO: disable autocomplete in forms


@require_http_methods(["GET"])
def connection_update_data(request, pk):

    if request.method == 'GET':
        exchange = Exchange.objects.filter(pk=pk)[0]
        api_connection = ApiConnection.objects.filter(broker=exchange).filter(owner=request.user)

        if(len(api_connection) == 0):
            raise Http404("Connot update connection data.")
  
        elif(len(api_connection) > 1):
            raise Http404("Connot update connection data, too many api connections.")
  
        elif(len(api_connection) == 1):
            client_tasks.import_balance(exchange, api_connection[0], request.user)    
        
        return HttpResponseRedirect(reverse('connection-detail', args=str(pk)))
