from django.urls import path
from . import views
from .views import connections_views, dashboard_views

urlpatterns = [
    path('', dashboard_views.index, name='index'),
    path('dashboard/', dashboard_views.DashboardView.as_view(), name='dashboard'),

    path('connections/', connections_views.ConnectionsView.as_view(), name='connections'),
    path('connections/<int:pk>/create', connections_views.AddConnectionModelForm.as_view(), name='add-connection'),
    path('connections/<int:pk>', connections_views.ConnectionInfoView.as_view(), name='connection-detail'),
    path('connections/<int:pk>/update-connection-data', connections_views.connection_update_data, name='update-connection-data'),

    path('pricehistory/', dashboard_views.PriceHistoryView.as_view(), name='pricehistory'),
]