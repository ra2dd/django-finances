from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy


from ..models import Portfolio, AssetBalance, Asset, Exchange, AssetBalanceHistory
from ..utils import dashboard_balance, assets_util
from ..forms import AssetBalanceHistoryForm

def get_user_portfolio(self):
    return get_object_or_404(Portfolio, owner=self.request.user)

class AssetListView(generic.ListView):
    
    template_name = 'assets/asset_list.html'
    model = Asset

    '''
    def get_queryset(self):
        queryset = Asset.objects.all()

        for asset in queryset:
            asset_balance_list = asset.assetbalance_set.filter(portfolio = )
    '''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        asset_list = context['object_list']
        for asset in asset_list:
            asset_balances = asset.assetbalance_set.filter(portfolio=get_user_portfolio(self)).filter(asset=asset)
            
            setattr(asset, 'value_object', assets_util.get_asset_value_object(asset_balances))

        return context
    

class AssetDetailView(generic.DetailView):
    template_name = 'assets/asset_detail.html'
    model = Asset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        asset_obj = context['object']

        asset_balances = asset_obj.assetbalance_set.filter(portfolio=get_user_portfolio(self)).filter(asset=asset_obj)
        
        setattr(asset_obj, 'value_object', assets_util.get_asset_value_object(asset_balances))

        return context


class ManualTradesListView(generic.ListView):
    template_name = 'assets/manualtrades_list.html'
    model = AssetBalance

    def get_queryset(self):
        exchange = Exchange.objects.filter(name='Manual Trades')[0]
        return (
            AssetBalance.objects
            .filter(portfolio=get_user_portfolio(self))
            .filter(broker=exchange)
        )
    

class AssetBalanceHistoryListView(generic.ListView):
    template_name = 'assets/assetbalancehistory_list.html'
    model = AssetBalanceHistory

    def get_queryset(self):
        return (
            AssetBalanceHistory.objects.filter(balance_id=self.kwargs['pk2'])
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['pk2'] = self.kwargs['pk2']

        return context


def assetbalancehistory_create(request, pk, pk2=None):
    """View function for creating assetbalancehistory records"""
    
    asset = get_object_or_404(Asset, pk=pk)

    if request.method == 'POST':

        # Create a form and populate it with the user entered data
        form = AssetBalanceHistoryForm(request.POST)

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
            return HttpResponseRedirect(reverse('asset-detail', args=[pk]))
    else:
        if pk2 == None:
            form = AssetBalanceHistoryForm()
        else:
            exchange_pk = get_object_or_404(AssetBalance, pk=pk2).broker.pk
            
            form = AssetBalanceHistoryForm(initial={'exchange': exchange_pk})

    context = {
        'form': form,
        'asset': asset,
    }

    return render(request, 'assets/assetbalancehistory_form.html', context)


class AssetBalanceHistoryDelete(generic.DeleteView):
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
                return reverse_lazy('asset-detail', args=str(self.kwargs['pk']))
            else:
                raise Http404('Error, please contact side admin.')
        except:
            return reverse_lazy('assetbalancehistory', args=[str(self.kwargs['pk']), str(self.kwargs['pk2'])])


