from django.views import generic

from ..models import Portfolio, AssetBalance, Asset, Exchange
from ..utils import dashboard_balance, assets_util

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
            portfolio = Portfolio.objects.filter(owner=self.request.user)[0]
            asset_balances = asset.assetbalance_set.filter(portfolio=portfolio).filter(asset=asset)
            
            setattr(asset, 'value_object', assets_util.get_asset_value_object(asset_balances))

        return context
    

class AssetDetailView(generic.DetailView):
    template_name = 'assets/asset_detail.html'
    model = Asset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        asset_obj = context['object']

        portfolio = Portfolio.objects.filter(owner=self.request.user)[0]
        asset_balances = asset_obj.assetbalance_set.filter(portfolio=portfolio).filter(asset=asset_obj)
        
        setattr(asset_obj, 'value_object', assets_util.get_asset_value_object(asset_balances))

        return context
