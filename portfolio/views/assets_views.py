from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from ..models import Portfolio, AssetBalance, Asset, Exchange, AssetBalanceHistory
from ..utils import dashboard_balance, assets_util
from ..forms import AssetPriceHistoryModelForm

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
        print(context)
        return context

def assetbalancehistory_create(request, pk, pk2='None'):
    """View function for creating assetbalancehistory records"""
    asset = get_object_or_404(Asset, pk=pk)
    print(request)
    if request.method == 'POST':

        # Create a form and populate it with the user entered data
        form = AssetPriceHistoryModelForm(request.POST)
        print(form)
        if form.is_valid():
            print('dziala')
            portfolio = get_object_or_404(Portfolio, owner=request.user)
            exchange = form.cleaned_data['exchange']
            assetbalance = AssetBalance.objects.filter(portfolio=portfolio).filter(broker=exchange).filter(asset=asset)

            if len(assetbalance) == 0:
                # Implement record creation
                raise Exception('error')
            
            amount = form.cleaned_data['amount']
            date = form.cleaned_data['date']
            assetbalancehistory_record = AssetBalanceHistory(amount=amount, date=date, balance=assetbalance[0])
            assetbalancehistory_record.save()
            
            print(assetbalancehistory_record)
            print('created record')
            return HttpResponseRedirect(reverse('asset-detail', args=[pk]))
    else:
        form = AssetPriceHistoryModelForm()

    context = {
        'form': form,
        'asset': asset,
    }

    return render(request, 'assets/assetbalancehistory_form.html', context)
