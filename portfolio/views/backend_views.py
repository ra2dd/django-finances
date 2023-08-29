from django.views import generic
from django.contrib.auth.mixins import PermissionRequiredMixin

from ..models import Asset


class AssetListView(generic.ListView, PermissionRequiredMixin):
    
    template_name = 'backend/asset_list.html'
    model = Asset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        return context