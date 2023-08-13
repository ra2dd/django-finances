from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic

from ..models import Exchange, ApiConnection
from ..tasks import client_tasks
from ..forms import AddConnectionModelForm

class ConnectionsView(generic.ListView, LoginRequiredMixin):
    """View function for listing user wallet connections"""

    template_name = 'connections/connections_list.html'
    model = Exchange

    def get_context_data(self, **kwargs):
        
        connection = ApiConnection.objects.filter(owner=self.request.user).filter(broker=Exchange.objects.filter(name='Binance')[0])[0] 
        api_key = connection.api_key
        secret_key = connection.secret_key

        #client_tasks.import_binance_balance(api_key, secret_key)
        client_tasks.check_binance_connection(api_key, secret_key)

        context = super().get_context_data(**kwargs)
        return context

class ConnectionInfoView(generic.DetailView, LoginRequiredMixin):
    """View function for displaying connection info"""
    model = Exchange
    template_name = 'connections/connection_detail.html'

class AddConnectionModelForm(generic.CreateView, LoginRequiredMixin):
    """View function for connecting user exchange data"""
    form_class = AddConnectionModelForm
    template_name = 'test.html'
