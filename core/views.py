from django.shortcuts   import render, get_object_or_404, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.core.paginator import Paginator

# Accueil
def home_view(request):
    messages = MessageAccueil.objects.all()[:3] 
    equipe = TeamMember.objects.all()[:5] 
    project = Projet.objects.all()[:5]
    
    return render(request, 'libis/home.html', {'messages': messages, 'equipe': equipe, 'projects': project})

# À propos
def about_view(request):
    equipe = TeamMember.objects.all()
    return render(request, 'libis/about.html', {'equipe': equipe})

# Contact
def contact_view(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        email = request.POST.get("email")
        sujet = request.POST.get("sujet")
        message = request.POST.get("message")
        ContactMessage.objects.create(nom=nom, email=email, sujet=sujet, message=message)
        return redirect('home')
    return render(request, 'libis/contact.html')

# Liste des services
def service_list_view(request):
    services = Service.objects.all()
    return render(request, 'libis/services.html', {'services': services})

# Détail d’un service
def service_detail_view(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'libis/service_detail.html', {'service': service})

# Liste des projets
def projet_list_view(request):
        # Récupérer tous les projets ou filtrer par catégorie si spécifié
    projet_list = Projet.objects.all()
    
    # # Pagination - 9 projets par page
    # paginator = Paginator(projet_list, 9)
    # page_number = request.GET.get('page')
   
    
    return render(request, 'libis/portfolio.html', {
        'projets': projet_list, 
    })

# Détail d’un projet
def projet_detail_view(request, slug):
    projet = get_object_or_404(Projet, slug=slug)
    return render(request, 'libis/projet_detail.html', {'projet': projet})

# Liste des articles du blog
def article_list_view(request):
    articles = Article.objects.all().order_by('-date_publication')
    return render(request, 'libis/blog.html', {'articles': articles})

# Détail d’un article
def article_detail_view(request, slug):
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'libis/article_detail.html', {'article': article})



# Liste des membres de l’équipe
def equipe_list_view(request):
    team_members = TeamMember.objects.all().order_by('nom')
    return render(request, 'libis/equipe.html', {'team_members': team_members})

# Détail d’un membre de l’équipe
def equipe_detail_view(request, pk):
    team_members = get_object_or_404(TeamMember, pk=pk)
    return render(request, 'libis/equipe_detail.html', {'team_members': team_members})



# Espace client : tableau de bord
@login_required
def client_dashboard_view(request):
    client = get_object_or_404(Client, user=request.user)
    fichiers = FichierPartagé.objects.filter(client=client)
    return render(request, 'libis/client_dashboard.html', {'client': client, 'fichiers': fichiers})

# Liste des fichiers partagés
@login_required
def file_list_view(request):
    client = get_object_or_404(Client, user=request.user)
    fichiers = FichierPartagé.objects.filter(client=client)
    return render(request, 'libis/file_list.html', {'fichiers': fichiers})

# Upload de fichier
@login_required
def file_upload_view(request):
    if request.method == "POST":
        titre = request.POST.get('titre')
        fichier = request.FILES.get('fichier')
        client = get_object_or_404(Client, user=request.user)
        FichierPartagé.objects.create(titre=titre, fichier=fichier, client=client)
        return HttpResponseRedirect(reverse('file_list'))
    return render(request, 'libis/file_upload.html')
