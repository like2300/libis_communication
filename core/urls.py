from django.urls import path, include
from .views import *

urlpatterns = [
    # core/urls.py
    path('', home_view, name='home'),
    path('a-propos/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),

    # services/urls.py
    path('services/', service_list_view, name='services'),
    path('services/<int:id>/', service_detail_view, name='service_detail'),

    # portfolio/urls.py
    path('portfolio/', projet_list_view, name='portfolio'),
    path('portfolio/<int:id>/', projet_detail_view, name='projet_detail'),

    # blog/urls.py
    path('blog/', article_list_view, name='blog'),
    path('blog/<slug:slug>/', article_detail_view, name='article_detail'),

    # clients/urls.py
    path('client/dashboard/', client_dashboard_view, name='clients'),
    path('client/files/', file_list_view, name='files'),
    path('client/upload/', file_upload_view, name='file_upload'),

]   