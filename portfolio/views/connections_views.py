from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied

from ..models import Exchange, ApiConnection, AssetBalance, AssetBalanceHistory
from ..utils import client_util
from ..forms import ConnectionAddModelForm

def fetch_exchange(self):
    return Exchange.objects.filter(pk=self.kwargs['pk'])[0]


class ExchangeListView(LoginRequiredMixin, generic.ListView):
    """View function for listing exchanges and their user wallet connections"""

    template_name = 'connections/exchange_list.html'
    model = Exchange

    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)
        
        obj_list = context['object_list']
        for obj in obj_list:
            setattr(obj, 'is_user_connected', obj.is_user_connected(self.request.user))

        return context


class ExchangeDetailView(LoginRequiredMixin, generic.DetailView):
    """View function for displaying exchange details and its user connection info"""
    model = Exchange
    template_name = 'connections/exchange_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        object = context['object']
        setattr(object, 'is_user_connected', object.is_user_connected(self.request.user))

        return context


class ApiConnectionAdd(LoginRequiredMixin, generic.CreateView):
    """View function for adding user ApiConnection to exchange"""

    model = ApiConnection
    form_class = ConnectionAddModelForm
    template_name = 'connections/apiconnection_add.html'

    # Send additional data to ModelForm
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['exchange_object'] = fetch_exchange(self)
        kwargs["user_object"] = self.request.user

        return kwargs
    
    # Set object additional fields after succesfully submitting a form
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.broker = fetch_exchange(self)
        self.object.owner = self.request.user
        self.object.save()

        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.broker.get_absolute_url()
    
    # Add context data to display in template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["exchange"] = fetch_exchange(self)

        return context

    # TODO: disable autocomplete in forms


class ApiConnectionDelete(LoginRequiredMixin, generic.DeleteView):
    model = ApiConnection
    template_name = 'connections/apiconnection_delete.html'

    def get_success_url(self):
        return self.object.broker.get_absolute_url()
        # return reverse_lazy('exchange-detail', args=str(self.kwargs['pk']))

    # Specify DeleteView context object
    def get_object(self):
        exchange = fetch_exchange(self)
        if exchange.name.lower() == 'manual trades':
            raise PermissionDenied
        
        object = ApiConnection.objects.filter(broker=exchange).filter(owner=self.request.user)[0]
        return object
    
    # Delete additional records when deleting a context object
    def form_valid(self, form):

        related_balance = AssetBalance.objects.filter(portfolio=self.request.user.portfolio).filter(broker=self.object.broker)

        for balance in related_balance:
            related_balance_history = AssetBalanceHistory.objects.filter(balance=balance)

            for balance_history in related_balance_history:
                balance_history.delete()

            balance.delete()

        return super().form_valid(self)


@login_required
@require_http_methods(["GET"])
def fetch_apiconnection_balance_view(request, pk):

    if request.method == 'GET':
        exchange = Exchange.objects.filter(pk=pk)[0]

        if exchange.name.lower() == 'manual trades':
            raise PermissionDenied

        api_connection = ApiConnection.objects.filter(broker=exchange).filter(owner=request.user)

        if(len(api_connection) == 0):
            raise Http404("Connot update connection data.")
  
        elif(len(api_connection) > 1):
            raise Http404("Connot update connection data, too many api connections.")
  
        elif(len(api_connection) == 1):
            client_util.import_balance(exchange, api_connection[0], request.user)    
        
        return HttpResponseRedirect(reverse('exchange-detail', args=str(pk)))
