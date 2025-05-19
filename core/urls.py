from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .forms import (
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    CustomPasswordChangeForm
)




# urls.py adminfrom django.contrib import admin


admin_urlpatterns = [
    path('dashboard/',  admin_dashboard_view, name='admin_dashboard'),
    path('clients/', admin_client_list_view, name='admin_client_list'),
    path('clients/create/',  admin_create_client_view, name='admin_create_client'),
    path('clients/requests/',  admin_client_requests_view, name='admin_client_requests'),
    path('projects/',  admin_client_projects_view, name='admin_client_projects'),
    path('team/',  admin_team_member_list_view, name='admin_team_member_list'),
    path('messages/',  admin_messages_list_view, name='admin_messages'),
    path('messages/send/', admin_send_message_view, name='admin_send_message'),
    path('reports/', admin_generate_report_view, name='admin_generate_report'),
    path('settings/',  admin_settings_view, name='admin_settings'),
    path('liste_clients',liste_clients,name="liste_clients"),
    path('article_list',article_list_view,name="article_list"),
    path('search_client/',admin_search_client_view,name="search_client"),
    path('mark_message/<int:message_id>/', mark_message_as_read, name='mark_message_as_read'),
]





# url for error handlers
handler400 = 'core.views.handler400'
handler403 = 'core.views.handler403'
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'

auth_urlpatterns = [
    # Authentification
    path('', RedirectView.as_view(url='/login/'), name='auth_redirect'),
    # Connexion
    path('login/', login_view, name='login'),
    
    # Déconnexion
    path('logout/', logout_view, name='logout'),
      
    
    # Réinitialisation de mot de passe
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='libis/password_reset.html',
        email_template_name='libis/password_reset_email.html',
        subject_template_name='libis/password_reset_subject.txt',
        form_class=CustomPasswordResetForm,
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),
    
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='libis/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='libis/password_reset_confirm.html',
            form_class=CustomSetPasswordForm,
            success_url=reverse_lazy('password_reset_complete')
        ), name='password_reset_confirm'),
    
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='libis/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Changement de mot de passe
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='libis/password_change.html',
        form_class=CustomPasswordChangeForm,
        success_url=reverse_lazy('password_change_done')
    ), name='password_change'),
    
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='libis/password_change_done.html'
    ), name='password_change_done'),
    
    # Inscription et vérification
    path('register/', register_view, name='register'),
    path('verify/<uuid:uuid>/', verify_email, name='verify_email'),
    path('verify-pending/', verify_pending_view, name='verify_pending'),
    path('resend-verification/', resend_verification, name='resend_verification'),
]

# URLs principales
urlpatterns = [
    # Pages principales
    path('', home_view, name='home'),
    path('a-propos/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),

    # Services
    path('services/', service_list_view, name='services'),
    path('services/<int:pk>/', service_detail_view, name='service_detail'),

    # Portfolio
    path('portfolio/', projet_list_view, name='portfolio'), 
    path('portfolio/<slug:slug>/', projet_detail_view, name='projet_detail'),

    # Équipe
    path('equipe/', equipe_list_view, name='equipe'),
    path('equipe/<int:pk>/', equipe_detail_view, name='equipe_detail'),
    
    # Blog
    path('blog/', article_list_view, name='blog'),
    path('blog/<slug:slug>/', article_detail_view, name='article_detail'),

    # Espace client
    path('client/dashboard/', client_dashboard_view, name='clients'),
    path('client/list_projects/', list_projects_view, name='list_projects'),
    path('client/upload/', file_upload_view, name='file_upload'),
    # path('client/complete-profile/', complete_client_profile, name='complete_client_profile'),
    path('client/edit-profile/', edit_profile_view, name='edit_client_profile'),
    path('client/create-project/', create_project_view, name='create_project'),
    
    path('projet/<int:pk>/edit/', edite_prod_user, name='edit_project'),
    
    path('projet/<int:pk>/', projet_detail_view, name='projet_detail_view'),

    path('projet/<int:pk>/delete/', delete_project, name='delete_project'),

    # Authentification (inclusion des URLs d'auth)
    path('accounts/', include(auth_urlpatterns)),

    # URL de l'admin
    path('administre/', include(admin_urlpatterns)),
     
]