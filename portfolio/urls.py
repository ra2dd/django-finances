from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('connections/', views.ConnectionsView.as_view(), name='connections')
]