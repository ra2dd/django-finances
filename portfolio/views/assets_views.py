from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from ..models import Portfolio, AssetBalance, Asset, Exchange, AssetBalanceHistory
from ..utils import assets_util
from ..forms import AssetBalanceHistoryForm

def get_user_portfolio(self):
    return get_object_or_404(Portfolio, owner=self.request.user)


class AssetListView(LoginRequiredMixin, generic.ListView):
    
    template_name = 'assets/asset_list.html'
    model = Asset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        asset_list = context['object_list']
        for asset in asset_list:
            asset_balances = asset.assetbalance_set.filter(portfolio=get_user_portfolio(self)).filter(asset=asset)
            
            setattr(asset, 'value_object', assets_util.get_asset_value_object(asset_balances, asset))

        return context
    

class AssetDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'assets/asset_detail.html'
    model = Asset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        asset_obj = context['object']

        user_assetbalance = asset_obj.assetbalance_set.filter(portfolio=get_user_portfolio(self)).filter(asset=asset_obj)
        context['user_assetbalance'] = user_assetbalance

        setattr(asset_obj, 'value_object', assets_util.get_asset_value_object(user_assetbalance, asset_obj))

        return context
   

class AssetBalanceHistoryListView(LoginRequiredMixin, generic.ListView):
    template_name = 'assets/assetbalancehistory_list.html'
    model = AssetBalanceHistory

    def get_queryset(self):
        balance = get_object_or_404(AssetBalance, pk=self.kwargs['pk2'])
        if balance.portfolio.owner == self.request.user:
            return AssetBalanceHistory.objects.filter(balance=balance)
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slug'] = self.kwargs['slug']
        context['pk2'] = self.kwargs['pk2']

        return context


@login_required
def assetbalancehistory_create(request, slug, pk2=None):
    """View function for creating assetbalancehistory records"""
    
    asset = get_object_or_404(Asset, slug=slug)

    exchange_choices = assets_util.get_exhange_choices()

    if request.method == 'POST':

        # Create a form and populate it with the user entered data
        form = AssetBalanceHistoryForm(request.POST, exchange_choices=exchange_choices)

        if form.is_valid():
            exchange = Exchange.objects.filter(pk=form.cleaned_data['exchange'])[0]
            amount = form.cleaned_data['amount']
            date = form.cleaned_data['date']
        
            portfolio = get_object_or_404(Portfolio, owner=request.user)
            assetbalance = AssetBalance.objects.filter(portfolio=portfolio).filter(broker=exchange).filter(asset=asset)

            # Check if AssetBalance exists
            # If it doesn't exist create new record
            if len(assetbalance) == 0:
                assetbalance_record = AssetBalance(portfolio=portfolio, asset=asset, broker=exchange)
                assetbalance_record.save()
            elif len(assetbalance) > 1:
                raise Http404('AssetBalance Error, please contact site admin.')
            else:
                assetbalance_record = assetbalance[0]
            
            # Check if AssetBalanceHistory exists with certain balance and date
            # If it exists delete existing record
            assetbalancehistory_exists = AssetBalanceHistory.objects.filter(balance=assetbalance_record).filter(date=date)
            if len(assetbalancehistory_exists) == 0:
                pass
            elif len(assetbalancehistory_exists) == 1:
                assetbalancehistory_exists[0].delete()
            elif len(assetbalancehistory_exists) > 1:
                raise Http404('AssetBalanceHistory Error, please contact site admin.')

            # Create new AssetBalanceHistory record
            assetbalancehistory_record = AssetBalanceHistory(amount=amount, date=date, balance=assetbalance_record)
            assetbalancehistory_record.save()

            return HttpResponseRedirect(reverse('assetbalancehistory', args=[slug, assetbalance_record.pk]))
    else:
        if pk2 == None:
            form = AssetBalanceHistoryForm(exchange_choices=exchange_choices)
        else:
            exchange_pk = get_object_or_404(AssetBalance, pk=pk2).broker.pk
            
            form = AssetBalanceHistoryForm(
                exchange_choices=exchange_choices, initial={'exchange': exchange_pk})

    context = {
        'form': form,
        'asset': asset,
    }

    return render(request, 'assets/assetbalancehistory_form.html', context)


class AssetBalanceHistoryDelete(LoginRequiredMixin, generic.DeleteView):
    model = AssetBalanceHistory
    template_name = 'assets/assetbalancehistory_delete.html'
    pk_url_kwarg = 'pk3'
    
    # Specify additional logic when deleting object
    def form_valid(self, form):

        if len(AssetBalanceHistory.objects.filter(balance=self.object.balance)) == 1:
            self.object.balance.delete()
            self.kwargs['balance_empty'] = True

        return super().form_valid(self)
    
    # If AssetBalanceHistory is empty redirect to asset-detail
    def get_success_url(self):
        try:
            if self.kwargs['balance_empty'] == True:
                return reverse_lazy('asset-detail', args=[str(self.kwargs['slug'])])
            else:
                raise Http404('Error, please contact side admin.')
        except:
            return reverse_lazy('assetbalancehistory', args=[str(self.kwargs['slug']), str(self.kwargs['pk2'])])


