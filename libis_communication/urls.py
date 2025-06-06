from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
 
 




urlpatterns = [
    # URL de l'admin
    path('admin/', admin.site.urls),
    # URL de l'admin Unfold
    path('', include('core.urls')),
]

# Servir les fichiers statiques et média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)