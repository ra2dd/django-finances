from django.urls import path
from . import views
from .views import connections_views, main_views, assets_views

urlpatterns = [
    path('', main_views.index, name='index'),
    path('dashboard/', main_views.DashboardView.as_view(), name='dashboard'),

    path('exchanges/', connections_views.ExchangeListView.as_view(), name='exchanges'),
    path('exchanges/<int:pk>', connections_views.ExchangeDetailView.as_view(), name='exchange-detail'),
    path('exchanges/<int:pk>/create-apiconnection', connections_views.ApiConnectionAdd.as_view(), name='apiconnection-add'),
    path('exchanges/<int:pk>/delete-apiconnection', connections_views.ApiConnectionDelete.as_view(), name='apiconnection-delete'),
    path('exchanges/<int:pk>/fetch-apiconnection-balance', connections_views.fetch_apiconnection_balance_view, name='fetch-apiconnection-balance'),

    path('assets/', assets_views.AssetListView.as_view(), name='assets'),
    path('assets/<int:pk>', assets_views.AssetDetailView.as_view(), name='asset-detail'),
    
    path('assets/<int:pk>/<int:pk2>', assets_views.AssetBalanceHistoryListView.as_view(), name='assetbalancehistory'),
    path('assets/<int:pk>/create', assets_views.assetbalancehistory_create, name='assetbalancehistory-create'),
    path('assets/<int:pk>/<int:pk2>/create', assets_views.assetbalancehistory_create, name='assetbalancehistory-create-pk2'),
    path('assets/<int:pk>/<int:pk2>/<int:pk3>/delete', assets_views.AssetBalanceHistoryDelete.as_view(), name='assetbalancehistory-delete'),
]