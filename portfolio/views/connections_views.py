from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic
from django.urls import reverse

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

    model = ApiConnection
    form_class = AddConnectionModelForm
    template_name = 'connections/connection_add.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.broker = Exchange.objects.filter(pk=self.kwargs['pk'])[0]
        self.object.owner = self.request.user
        self.object.save()

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('connection-detail', args=[str(self.kwargs['pk'])])
        
    
