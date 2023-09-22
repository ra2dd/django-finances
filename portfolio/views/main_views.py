from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from ..utils import dashboard_util
     
     
def index(request):
    """View function for the home page of the site."""

    context = {}

    return render(request, 'index.html', context=context)


class DashboardView(generic.TemplateView, LoginRequiredMixin):
    """View function for the user dashboard"""

    template_name = 'dashboard.html'

    def get_context_data(self):
        return dashboard_util.get_dashboard_context(self.request.user)

        """
        TODO:
            check if price history values are duplicated in calculating user daily total balance list
        """

class DemoView(generic.TemplateView):
    """View for showcasing app dashboard with demo data."""

    template_name = 'dashboard.html'

    def get_context_data(self):
        demo_user = get_object_or_404(User, username='demo')

        # dashboard_util.create_test_user_data(demo_user)

        return dashboard_util.get_dashboard_context(demo_user)

        