from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
import logging
import uuid 
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import *
from .forms import *  
import csv
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.admin.views.decorators import staff_member_required
from .forms import AdminClientForm, AdminProjectForm, AdminTeamMemberForm, AdminMessageReplyForm
from django.db.models import Count
from django.contrib.auth.decorators import login_required
# Activités récentes (version améliorée)
from django.contrib.admin.models import LogEntry
from django.http import JsonResponse
# ============= admin views ==============





# Helper pour vérifier si l'utilisateur est admin
def is_admin(user):
    return user.is_superuser or (hasattr(user, 'is_staff') and user.is_staff)

@staff_member_required
def liste_clients(request):
    clients = Client.objects.all()
    stats = {
        'total_clients': clients.count(),
        'active_projects': Projets_user.objects.count(),
        'pending_messages': ContactMessage.objects.filter(traite=False).count(),
        'team_members': TeamMember.objects.count(),
        'portfolio_projects_count': Projet.objects.count()
    }
    admin_log = LogEntry.objects.select_related('user').order_by('-action_time')[:10]
    
    quick_actions = [
        {'title': 'Ajouter Client', 'url': 'admin_create_client', 'icon': 'user-plus'},
        {'title': 'Créer Projet', 'url': 'admin_client_projects', 'icon': 'folder-plus'},
        {'title': 'Envoyer Message', 'url': 'admin_send_message', 'icon': 'envelope'},
    ]

    context = {
        'clients': clients,
        'stats': stats,
        'admin_log': admin_log,
        'quick_actions': quick_actions,
        'page_title': _('Liste des clients')
    }

    return render(request, 'admin/liste_clients.html', context)
# ============= admin views ==============
 
@staff_member_required
def admin_dashboard_view(request):
    stats = {
        'total_clients': Client.objects.count(),
        'active_projects': Projets_user.objects.count(),
        'pending_messages': ContactMessage.objects.filter(is_read=False).order_by('-date').count(),
        'team_members': TeamMember.objects.count(),
        'portfolio_projects_count': Projet.objects.count(),
    }

    admin_log = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:10]
    
    quick_actions = [
        {'title': 'Ajouter Client', 'url': 'admin_create_client', 'icon': 'user-plus'},
        {'title': 'Créer Projet', 'url': 'admin_client_projects', 'icon': 'folder-plus'},
        {'title': 'Envoyer Message', 'url': 'admin_send_message', 'icon': 'envelope'},
    ]
   
    # Corrected queryset using 'date' instead of 'date_debut'
    project_list = Projets_user.objects.select_related('client').all() 
    paginator = Paginator(project_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'total_clients': stats['total_clients'],
        'active_projects': stats['active_projects'],
        'pending_messages': stats['pending_messages'],
        'admin_log': admin_log,
        'quick_actions': quick_actions,
        'page_title': _('Tableau de bord administratif'),
        'portfolio_projects_count': stats['portfolio_projects_count'],
        'team_members': stats['team_members'],
        'page_obj': page_obj
    }
    
    return render(request, 'admin/dashboard.html', context)
@staff_member_required
def article_list_view(request):
    articles = Article.objects.all().order_by('-date_publication')
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/articles.html', {
        'page_obj': page_obj,
        'user': request.user
    })

@staff_member_required
def admin_client_projects_view(request):
    clients = Client.objects.annotate(
        projets_user_count=Count('fichiers')  # Utilisez le related_name correct
    ).prefetch_related('fichiers').order_by('-projets_user_count')
    
    # Pagination
    paginator = Paginator(clients, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'active_projects': Projets_user.objects.filter(
            Q(date_fin__gte=timezone.now()) | Q(date_fin__isnull=True)
        ).select_related('client'),
        'active_projects_count': Projets_user.objects.filter(
            Q(date_fin__gte=timezone.now()) | Q(date_fin__isnull=True)
        ).count(),
        'portfolio_projects_count': Projet.objects.count(),
        'page_title': _('Projets clients'),
        'can_add_project': request.user.has_perm('core.add_projets_user')
    }
    return render(request, 'admin/client_projects.html', context)

@staff_member_required
def admin_team_member_list_view(request):
    team = TeamMember.objects.all().order_by('nom')
    return render(request, 'admin/team_list.html', {
        'team': team,
        'page_title': _('Gestion de l\'équipe')
    })

@staff_member_required
def admin_messages_list_view(request):
    messages = ContactMessage.objects.filter(is_read=False).order_by('-date')
    
    return render(request, 'admin/messages_list.html', {
        
        'processed_messages': messages 
        
    })


@staff_member_required
def mark_message_as_read(request, message_id):
    try:
        message = ContactMessage.objects.get(id=message_id)
        message.is_read = True
        message.save()
        return JsonResponse({'status': 'success'})
    except ContactMessage.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

@staff_member_required
def admin_settings_view(request):
    info = Info.objects.first()
    
    if request.method == 'POST':
        # Créer ou mettre à jour l'objet Info
        if info:
            form_data = request.POST.copy()
            form_data['photo'] = request.FILES.get('photo', info.photo)
            
            # Gérer les champs de réseaux sociaux
            social_fields = ['lien_linkedin', 'lien_twitter', 'lien_facebook', 'lien_instagram']
            for field in social_fields:
                value = form_data.get(field, '')
                if value and not value.startswith('http'):
                    form_data[field] = f'https://{field.replace("lien_", "")}.com/{value}'
            
            # Mettre à jour l'objet existant
            for field, value in form_data.items():
                setattr(info, field, value)
            info.save()
        else:
            # Créer un nouvel objet Info
            info = Info.objects.create(
                nom=request.POST.get('nom'),
                bio=request.POST.get('bio'),
                photo=request.FILES.get('photo'),
                lien_email=request.POST.get('lien_email'),
                lien_telephone=request.POST.get('lien_telephone'),
                lien_linkedin=request.POST.get('lien_linkedin'),
                lien_twitter=request.POST.get('lien_twitter'),
                lien_facebook=request.POST.get('lien_facebook'),
                lien_instagram=request.POST.get('lien_instagram')
            )
        
        messages.success(request, _("Les paramètres ont été mis à jour avec succès"))
        return redirect('admin_settings')
    
    return render(request, 'admin/settings.html', {
        'info': info or Info(),  # Passe un objet vide si aucun n'existe
        'page_title': _('Paramètres du site')
    })


@staff_member_required
def admin_search_client_view(request):
    query = request.GET.get('q', '').strip()
    results = {'query': query}
    
    if query and len(query) > 2:
        results.update({
            'clients': Client.objects.filter(
                Q(entreprise__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query)
            )[:5],
            'projects': Projet.objects.filter(
                Q(titre__icontains=query) |
                Q(description__icontains=query)
            )[:5],
            'messages': ContactMessage.objects.filter(
                Q(nom__icontains=query) |
                Q(email__icontains=query) |
                Q(sujet__icontains=query) |
                Q(message__icontains=query)
            )[:5],
            'team': TeamMember.objects.filter(
                Q(nom__icontains=query) |
                Q(poste__icontains=query)
            )[:3],
            'user_projects': Projets_user.objects.filter(
                Q(titre__icontains=query) |
                Q(description__icontains=query)
            )[:5]
        })
    
    return render(request, 'admin/search_client.html', results)


# Fonctions utilitaires
def get_recent_activities():
    """Récupère les activités récentes pour le dashboard"""
    activities = []
    
    # Derniers clients ajoutés
    last_clients = Client.objects.order_by('-date_joined')[:3]
    for client in last_clients:
        activities.append({
            'type': 'client',
            'title': f"Nouveau client: {client.name}",
            'date': client.date_joined,
            'icon': 'user-plus'
        })
    
    # Derniers projets
    last_projects = Projet.objects.order_by('-created_at')[:2]
    for project in last_projects:
        activities.append({
            'type': 'project',
            'title': f"Projet créé: {project.title}",
            'date': project.created_at,
            'icon': 'folder-plus'
        })
    
    # Trier toutes les activités par date
    return sorted(activities, key=lambda x: x['date'], reverse=True)[:5]
 
@staff_member_required
def admin_activity_log_view(request):
    """JSON endpoint for recent activities"""
    from django.contrib.admin.models import LogEntry
    from django.core.serializers.json import DjangoJSONEncoder
    import json
    from django.http import JsonResponse
    
    activities = LogEntry.objects.all().order_by('-action_time')[:10]
    
    data = {
        'activities': [
            {
                'message': entry.get_change_message(),
                'time': entry.action_time.strftime("%Y-%m-%d %H:%M"),
                'user': str(entry.user),
                'action': entry.get_action_flag_display(),
            }
            for entry in activities
        ]
    }
    
    return JsonResponse(data, encoder=DjangoJSONEncoder)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_create_client_view(request):
    if request.method == "POST":
        form = AdminClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            # Création d'un utilisateur par défaut ou associé si nécessaire
            user = User.objects.create_user(
                username=form.cleaned_data['entreprise'].lower().replace(" ", "_"),
                email=f"{form.cleaned_data['entreprise'].lower().replace(' ', '_')}@example.com",
                password=User.objects.make_random_password(),
                is_client=True,
                email_verified=True
            )
            client.user = user
            client.save()
            messages.success(request, _("Le client a été créé avec succès."))
            return redirect('admin_client_list')
    else:
        form = AdminClientForm()

    context = {
        'form': form,
        'title': _('Créer un nouveau client')
    }
    return render(request, 'libis/admin/clients/create.html', context)




class AdminSendMessageForm(forms.Form):
    sujet = forms.CharField(label=_("Sujet"), max_length=150)
    message = forms.CharField(label=_("Message"), widget=forms.Textarea())
    destinataire = forms.EmailField(label=_("Email du destinataire"))


@staff_member_required
@require_http_methods(["GET", "POST"])
def admin_send_message_view(request):
    if request.method == "POST":
        destinataire = request.POST.get('destinataire')
        sujet = request.POST.get('sujet')
        message = request.POST.get('message')

        if not all([destinataire, sujet, message]):
            messages.error(request, _("Tous les champs sont obligatoires"))
        else:
            try:
                send_mail(
                    subject=sujet,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[destinataire],
                    fail_silently=False,
                )
                messages.success(request, _("Le message a été envoyé avec succès"))
                return redirect('admin_messages')
            except Exception as e:
                messages.error(request, _("Erreur lors de l'envoi du message: ") + str(e))

    return render(request, 'admin/messages/send.html', {
        'page_title': _('Envoyer un message')
    })

@login_required
@user_passes_test(is_admin)
def admin_generate_report_view(request):
    report_type = request.GET.get('type', 'clients')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{timezone.now().date()}.csv"'

    writer = csv.writer(response)

    if report_type == 'clients':
        writer.writerow(['Entreprise', 'Téléphone', 'Email', 'Adresse', 'Date d\'inscription'])
        clients = Client.objects.all().select_related('user')
        for client in clients:
            writer.writerow([
                client.entreprise,
                client.telephone,
                client.user.email,
                client.adresse,
                client.date_inscription.strftime("%d/%m/%Y")
            ])
    elif report_type == 'messages':
        writer.writerow(['Nom', 'Email', 'Sujet', 'Date', 'Traité'])
        messages_db = ContactMessage.objects.all()
        for msg in messages_db:
            writer.writerow([
                msg.nom,
                msg.email,
                msg.sujet,
                msg.date.strftime("%d/%m/%Y %H:%M"),
                "Oui" if msg.traite else "Non"
            ])

    return response
 

# views.py

@login_required
@user_passes_test(is_admin)
def admin_client_requests_view(request):
    # Exemple de modèle : Projets_user pour les projets soumis par les clients
    requests_list = Projets_user.objects.select_related('client').order_by('-date_ajout')
    
    paginator = Paginator(requests_list, 10)  # 10 demandes par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': _('Demandes clients')
    }
    return render(request, 'libis/admin/clients/requests.html', context)


@staff_member_required 
def admin_client_list_view(request):
    clients = Client.objects.annotate(
        project_count=Count('fichiers')  # Utilisez le nom correct de la relation
    ).prefetch_related('user').order_by('-date_inscription')
    
    paginator = Paginator(clients, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/clients/list.html', {
        'page_obj': page_obj,
        'page_title': _('Liste des clients')
    })
# ============== end =====================












User = get_user_model()
logger = logging.getLogger(__name__)

# Helpers
def get_client_or_404(user):
    """Helper to get client or return 404 with proper messaging"""
    try:
        return Client.objects.get(user=user)
    except Client.DoesNotExist:
        logger.warning(f"Client profile missing for user {user.username}")
        raise PermissionDenied(_("Client profile not found"))

# Public Views
 
def home_view(request):
    """Homepage with featured content"""
    context = {
        'messages': MessageAccueil.objects.filter(actif=True)[:3],
        'equipe': TeamMember.objects.all()[:5],
        'projets': Projet.objects.filter(en_avant=True)[:5],
        # name user connected 
        'user': request.user
    }
    return render(request, 'libis/home.html', context)

@cache_page(60 * 60)  # Cache for 1 hour
def about_view(request):
    """About page with team information"""
    context = {
        'equipe': TeamMember.objects.all().order_by('?'),  # Random order
        'informations': Info.objects.first(),
    }
    return render(request, 'libis/about.html', context)

@require_http_methods(["GET", "POST"])
@csrf_protect
def contact_view(request):
    """Contact form view"""
    info = Info.objects.all()
    
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                ContactMessage.objects.create(**form.cleaned_data)
                messages.success(request, _("Your message has been sent successfully!"))
                logger.info(f"New contact message from {form.cleaned_data['email']}")
                return redirect('home')
            except Exception as e:
                logger.error(f"Contact form error: {str(e)}")
                messages.error(request, _("An error occurred while sending your message"))
        else:
            messages.error(request, _("Please correct the errors in the form"))
    else:
        form = ContactForm()

    return render(request, 'libis/contact.html', {'info': info, 'form': form,'user': request.user})

@cache_page(60 * 60 * 2)  # Cache for 2 hours
def service_list_view(request):
    """List all services"""
    services = Service.objects.all().order_by('ordre')
    return render(request, 'libis/services.html', {'services': services,'user': request.user})

def service_detail_view(request, slug):
    """Service detail page"""
    service = get_object_or_404(Service, slug=slug)
    related_services = Service.objects.filter(
        categorie=service.categorie
    ).exclude(id=service.id)[:3]
    
    context = {
        'service': service,
        'related_services': related_services,
        'user': request.user
    }
    return render(request, 'libis/service_detail.html', context)

def projet_list_view(request):
    """Portfolio project listing with pagination"""
    projet_list = Projet.objects.all().order_by('-date')
    paginator = Paginator(projet_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'libis/portfolio.html', {'page_obj': page_obj,'user': request.user})
 




@login_required
def projet_detail_view(request, slug):
    try:
        projet = get_object_or_404(Projets_user, slug=slug)
        
        # Verify the requesting user owns this project
        if request.user != projet.client.user:
            raise PermissionDenied
        
        context = {
            'projet': projet,
            'user': request.user
        }
        return render(request, 'libis/projet-detail.html', context)
        
    except Projets_user.DoesNotExist:
        logger.warning(f"Project not found: {slug}")
        return render(request, 'libis/404.html', {'message': 'Project not found'}, status=404)
    except PermissionDenied:
        logger.warning(f"Unauthorized access to project {slug} by user {request.user}")
        return render(request, 'libis/403.html', status=403)
    
    
def article_list_view(request):
    """Blog article listing"""
    articles = Article.objects.all().order_by('-date_publication')
    return render(request, 'libis/blog.html', {'articles': articles,'user': request.user})

def article_detail_view(request, slug):
    """Article detail page"""
    article = get_object_or_404(Article, slug=slug)
    article.increment_views()  # If you have a view counter method
    
    context = {
        'article': article,
        'related_articles': Article.get_related_articles(article)[:3],
        'user': request.user
    }
    return render(request, 'libis/article_detail.html', context)

def equipe_list_view(request):
    """Team member listing"""
    team_members = TeamMember.objects.all().order_by('nom')
    return render(request, 'libis/equipe.html', {'team_members': team_members,'user': request.user})

def equipe_detail_view(request, pk):
    """Team member detail"""
    team_member = get_object_or_404(TeamMember, pk=pk)
    return render(request, 'libis/detail_equipe.html', {'team_member': team_member,'user': request.user})

def search_view(request):
    """Global search functionality"""
    query = request.GET.get('q', '').strip()
    results = {'query': query}
    
    if query and len(query) > 2:  # Minimum search length
        results.update({
            'projets': Projet.objects.search(query)[:5],
            'articles': Article.objects.search(query)[:5],
            'services': Service.objects.search(query)[:5],
            'team': TeamMember.objects.search(query)[:3],
            'user': request.user
        })
    
    return render(request, 'libis/search.html', results)











def custom_authenticate(username_or_email, password):
    username = username_or_email
    if '@' in username_or_email:
        try:
            user = User.objects.get(email__iexact=username_or_email)
            username = user.get_username()
        except User.DoesNotExist:
            return None
    return authenticate(username=username, password=password)

# Authentication Views

@require_http_methods(["GET", "POST"])
@csrf_protect
def login_view(request):
    """Vue de connexion utilisateur"""
    if request.user.is_authenticated:
        return redirect('client/dashboard')  # Rediriger si l'utilisateur est déjà authentifié 
    if request.method == 'POST':
        form = LoginForm(request.POST)  # Utilisation du formulaire personnalisé

        if form.is_valid():  # Vérification si le formulaire est valide
            username_or_email = form.cleaned_data['username']  # Récupérer l'email ou le nom d'utilisateur
            password = form.cleaned_data['password']  # Récupérer le mot de passe

            # Utilisation de la méthode custom_authenticate pour authentifier l'utilisateur
            user = custom_authenticate(username_or_email, password)

            if user is not None:
                if user.is_active:
                    login(request, user)  # Connexion de l'utilisateur
                    messages.success(request, _("Bienvenue de retour !"))  # Message de bienvenue
                    next_url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)  # Récupérer l'URL "next" si présente
                    return redirect(next_url)  # Redirection après la connexion
                else:
                    messages.error(request, _("Ce compte est inactif."))  # Si l'utilisateur est inactif
            else:
                messages.error(request, _("Identifiants invalides."))  # Si l'utilisateur n'est pas trouvé
    else:
        form = LoginForm()  # Si la méthode est GET, on affiche le formulaire vide

    return render(request, 'libis/login.html', {'form': form})  # Rendu du template avec le formulaire

def send_verification_email(user):
    """Send email verification with secure token"""
    verification_link = f"{settings.DOMAIN}/accounts/verify/{user.verification_uuid}/"
    subject = _("Confirm your email address")
    message = render_to_string('libis/email_verification.html', {
        'user': user,
        'verification_link': verification_link
    })
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=message,
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        raise


@require_http_methods(["GET", "POST"])
@csrf_protect
def register_view(request):
    if request.user.is_authenticated:
        # profil complet
        if hasattr(request.user, 'client'):
            return redirect('client_dashboard')
        # profil incomplet
        else:
            return redirect('edit_profile')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                # Process registration
                user = form.save()  # This includes client creation
                
                # Send verification email
                try:
                    send_verification_email(user)
                    messages.success(request, _("Registration successful! Please check your email."))
                    return redirect('login')
                except Exception as email_error:
                    logger.error(f"Email sending failed: {str(email_error)}")
                    messages.warning(request, _("Account created but verification email failed."))
                    return redirect('register')
                    
            except ValidationError as e:
                messages.error(request, e.message)
            except Exception as e:
                logger.error(f"Registration failed: {str(e)}", exc_info=True)
                messages.error(request, _("System error during registration. Please try again."))
        else:
            # Afficher les erreurs de formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = RegisterForm()
    
    return render(request, 'libis/register.html', {'form': form})

def verify_email(request, uuid):
    """Email verification endpoint with automatic cleanup"""
    try:
        user = get_object_or_404(User, verification_uuid=uuid)
        
        # Vérifier si le lien a expiré (30 minutes)
        expiration_time = user.date_joined + timedelta(minutes=30)
        
        if timezone.now() > expiration_time:
            # Supprimer l'utilisateur si le lien a expiré
            email = user.email
            user.delete()
            logger.warning(f"User {email} deleted due to expired verification link")
            messages.error(request, _("Verification link has expired. Please register again."))
            return redirect('register')
            
        if not user.email_verified:
            # Marquer l'email comme vérifié
            user.email_verified = True
            user.is_active = True
            user.save()
            
            # Connecter l'utilisateur
            login(request, user)
            messages.success(request, _("Email successfully verified!"))
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.info(request, _("Email already verified"))
            
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        messages.error(request, _("Invalid verification link"))
    
    return redirect(settings.LOGIN_REDIRECT_URL)

def verify_pending_view(request):
    """Email verification pending page"""
    return render(request, 'libis/verify_pending.html')

@login_required
def resend_verification(request):
    """Resend verification email"""
    if not request.user.email_verified:
        request.user.verification_uuid = uuid.uuid4()
        request.user.save()
        send_verification_email(request.user)
        messages.info(request, _("Verification email resent!"))
    return redirect('home')

@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, _("You have been logged out"))
    return redirect(settings.LOGOUT_REDIRECT_URL)

# Client Dashboard Views
@login_required
def client_dashboard_view(request):
    """Secure client dashboard view"""
    try:
        client = get_object_or_404(Client, user=request.user)
        print(client)
        context = {
            'client': client,
            # 'unread_messages': Message.objects.unread_for(request.user)[:3],
            'user': request.user
        }
        return render(request, 'libis/client_dashboard.html', context)
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        messages.error(request, _("Cannot load dashboard."))
        return redirect('home')

 
@login_required
def create_project_view(request):
    """Create a new client project file"""
    client = get_client_or_404(request.user)
    
    if request.method == 'POST':
        form = Projets_userForms(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            try:
                projet = form.save(commit=False)
                projet.client = client  # Set the client relationship
                 # Génère un slug à partir du titre

                #  send email to client confimation creation project user
                
                send_mail(
                    subject=f"Confirmation de création de projet {projet.titre}",
                    message=f"Bonjour {client.user.first_name}, nous avons bien reçu votre demande de création de projet {projet.titre}. Veuillez consulter votre projet sur le site.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.user.email],
                    fail_silently=False,
                )


                
                projet.save()
                messages.success(request, _("Project file uploaded successfully!"))
                logger.info(f"Project file uploaded by {request.user.username}: {projet.titre}")
                return redirect('client_dashboard')
            except Exception as e:
                logger.error(f"Project file upload error: {str(e)}")
                messages.error(request, _("Project file upload failed"))
        else:
            # Show form errors to user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = Projets_userForms()
    
    return render(request, 'libis/create_project.html', {
        'form': form,
        'client': client
    })

@login_required
@require_http_methods(["GET", "POST"])
@csrf_protect
def file_upload_view(request):
    """File upload view for clients"""
    client = get_client_or_404(request.user)
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                fichier = form.save(commit=False)
                fichier.client = client
                fichier.save()
                messages.success(request, _("File uploaded successfully!"))
                logger.info(f"File uploaded by {request.user.username}: {fichier.titre}")
                return redirect('file_list')
            except Exception as e:
                logger.error(f"File upload error: {str(e)}")
                messages.error(request, _("File upload failed"))
        else:
            messages.error(request, _("Invalid file upload"))
    else:
        form = FileUploadForm()
    
    return render(request, 'libis/file_upload.html', {'form': form})

@login_required
def edit_profile_view(request):
    """Client profile editing"""
    client = get_client_or_404(request.user)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        client_form = ClientEditForm(request.POST, instance=client)
        
        if user_form.is_valid() and client_form.is_valid():
            user_form.save()
            client.profile_complete = True
            client_form.save()
            messages.success(request, _("Profile updated successfully!"))
            return redirect('clients')
    else:
        user_form = UserEditForm(instance=request.user)
        client_form = ClientEditForm(instance=client)
    
    return render(request, 'libis/edit_profile.html', {
        'user_form': user_form,
        'client_form': client_form,
        'client': client,
    })


@login_required
def list_projects_view(request):
    """List all project files for the client"""
    client = get_client_or_404(request.user)
    
    # Use date_ajout (creation timestamp) for ordering
    projets = Projets_user.objects.filter(client=client).order_by('-date_ajout')
    
    # Add pagination
    paginator = Paginator(projets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'libis/list_projects.html', {
        'page_obj': page_obj,
        'client': client
    })
 
# 
# Error Handlers
def handler400(request, exception):
    logger.warning(f"Bad request: {str(exception)}")
    return render(request, '400.html', status=400)

def handler403(request, exception):
    logger.warning(f"Permission denied: {str(exception)}")
    return render(request, '403.html', status=403)

def handler404(request, exception):
    logger.warning(f"Page not found: {str(exception)}")
    return render(request, '404.html', status=404)

def handler500(request):
    logger.error("Server error occurred")
    return render(request, '500.html', status=500) 










def dashboard_callback(request, context):
    context.update({
        "custom_variable": "value",
    })

    return context




@login_required 
def edite_prod_user(request, pk):
    projet = get_object_or_404(Projets_user, pk=pk)
    
    if request.method == 'POST':
        form = Projets_userForms(request.POST, request.FILES, instance=projet)  # N'oubliez pas l'instance!
        if form.is_valid():
            form.save()
            messages.success(request, _("Projet mis à jour avec succès"))
            return redirect('list_projects')
    else:
        form = Projets_userForms(instance=projet)
    
    return render(request, 'libis/edit_projet.html', {
        'form': form,
        'projet': projet,
        'user': request.user
    })
 






@login_required
def delete_project(request, pk):
    if request.method == 'POST':
        projet = get_object_or_404(Projets_user, pk=pk, client=request.user.client)
        projet.delete()
        messages.success(request, "Le projet a été supprimé avec succès.")
        return redirect('list_projects')
    else:
        return redirect('list_projects')