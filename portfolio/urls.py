from django.urls import path
from . import views
from .views import connections_views, dashboard_views

urlpatterns = [
    path('', dashboard_views.index, name='index'),
    path('dashboard/', dashboard_views.DashboardView.as_view(), name='dashboard'),

    path('exchanges/', connections_views.ExchangeListView.as_view(), name='exchanges'),
    path('exchanges/<int:pk>', connections_views.ExchangeDetailView.as_view(), name='exchange-detail'),
    path('exchanges/<int:pk>/create-apiconnection', connections_views.ApiConnectionAdd.as_view(), name='apiconnection-add'),
    path('exchanges/<int:pk>/delete-apiconnection', connections_views.ApiConnectionDelete.as_view(), name='apiconnection-delete'),
    path('exchanges/<int:pk>/fetch-apiconnection-balance', connections_views.fetch_apiconnection_balance_view, name='fetch-apiconnection-balance'),

    path('pricehistory/', dashboard_views.PriceHistoryView.as_view(), name='pricehistory'),
]