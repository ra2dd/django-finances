from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from ..utils import dashboard_util
     
     
def index(request):
    """View function for the home page of the site."""

    return render(request, 'index.html', {})


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    """View function for the user dashboard"""

    dashboard_service = None
    template_name = 'dashboard.html'
        
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.dashboard_service = dashboard_util.DashboardService(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self):
        return self.dashboard_service.get_dashboard_context()

        """
        TODO:
            check if price history values are duplicated in calculating user daily total balance list
        """

class DemoView(generic.TemplateView):
    """View for showcasing app dashboard with demo data."""

    dashboard_service = None
    template_name = 'dashboard.html'
        
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        demo_user = get_object_or_404(User, username='demo')
        self.dashboard_service = dashboard_util.DashboardService(demo_user)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self):
        return self.dashboard_service.get_dashboard_context()    