from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    # core/urls.py
    path('', home_view, name='home'),
    path('a-propos/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
   

    # services/urls.py
    path('services/', service_list_view, name='services'),
    path('services/<int:pk>/', service_detail_view, name='service_detail'),

    # portfolio/urls.py
    path('portfolio/', projet_list_view, name='portfolio'), 
    path('portfolio/<slug:slug>/', projet_detail_view, name='projet_detail'),
    
    # blog/urls.py
    path('blog/', article_list_view, name='blog'),
    path('blog/<slug:slug>/', article_detail_view, name='article_detail'),

    # clients/urls.py
    path('client/dashboard/', client_dashboard_view, name='clients'),
    path('client/files/', file_list_view, name='files'),
    path('client/upload/', file_upload_view, name='file_upload'),

    # # account_login
    # path('accounts/login/', auth_views.LoginView.as_view(template_name='libis/login.html'), name='login'),
    # path('accounts/logout/', auth_views.LogoutView.as_view(template_name='libis/logout.html'), name='logout'),
    # path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='libis/password_reset.html'), name='password_reset'),
    # path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='libis/password_reset_done.html'), name='password_reset_done'),
    # path('accounts/password_reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='libis/password_reset_confirm.html'), name='password_reset_confirm'),
    # path('accounts/password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='libis/password_reset_complete.html'), name='password_reset_complete'),
    # path('accounts/signup/', auth_views.RegisterView.as_view(template_name='libis/register.html'), name='register'),
    # path('accounts/activate/<uidb64>/<token>/', auth_views.ActivationView.as_view(template_name='libis/activation.html'), name='activation'),
    

]   