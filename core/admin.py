from django.contrib import admin
from .models import *

# Admin de l’équipe
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('nom', 'poste', 'photo')
    search_fields = ('nom', 'poste')

# Admin des messages de contact
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'sujet', 'date')
    search_fields = ('nom', 'email', 'sujet')

# Admin des services
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'description', 'icone', 'categorie')
    search_fields = ('titre', 'description', 'icone', 'categorie')

# Admin des projets
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'description', 'image', 'categorie')
    search_fields = ('titre', 'description', 'image', 'categorie')

# Admin des articles
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'date_publication')
    search_fields = ('titre', 'auteur', 'date_publication')

# Admin des clients
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'entreprise', 'email')
    search_fields = ('user', 'entreprise', 'email')

# Admin des fichiers partagés
class FichierPartagéAdmin(admin.ModelAdmin):
    list_display = ('titre', 'fichier', 'client')
    search_fields = ('titre', 'fichier', 'client')

class HomeAdmin(admin.ModelAdmin):
    list_display = ('titre', 'contenu', 'media')
    search_fields = ('titre', 'contenu', 'media')

# Admin général

admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Projet, ProjetAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(FichierPartagé, FichierPartagéAdmin)
admin.site.register(MessageAccueil, HomeAdmin)
