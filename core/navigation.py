# core/navigation.py
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.conf import settings
def get_navigation(request):
    return [
        {
            "title": "Navigation",
            "separator": True,
            "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link":  reverse_lazy('admin_dashboard'),
                     
                    },

                    {
                        "title": "Mes Projets",
                        "icon": "folder",
                        "link":  reverse_lazy('admin_client_projects'),
                    },

                    
 
                    
          
            ],
        }
    ]