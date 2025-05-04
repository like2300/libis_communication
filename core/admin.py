from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import *

# Personnalisation du thème admin
class CustomAdminSite(AdminSite):
    site_header = 'Libis Communication'
    site_title = 'Libis Communication'
    index_title = 'Accueil'
    
    def each_context(self, request):
        context = super().each_context(request)
        # Couleurs personnalisées
        context['site_header_color'] = 'white'
        context['site_title_color'] = 'white'
        context['background_color'] = '#111'
        context['sidebar_bg'] = '#8B0000'  # Rouge foncé
        context['sidebar_text'] = 'white'
        context['sidebar_link'] = 'white'
        return context

# Utilisation du site admin personnalisé
admin_site = CustomAdminSite(name='custom_admin')

# CSS personnalisé pour l'admin
class CustomAdminCSS(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

# Admin de l'équipe
class TeamMemberAdmin(CustomAdminCSS, admin.ModelAdmin):
    list_display = ('nom', 'poste', 'photo_preview')
    search_fields = ('nom', 'poste')
    list_filter = ('poste',)
    
    def photo_preview(self, obj):
        from django.utils.html import format_html
        if obj.photo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.photo.url)
        return "-"
    photo_preview.short_description = 'Photo'

# Admin des messages de contact
class ContactMessageAdmin(CustomAdminCSS, admin.ModelAdmin):
    list_display = ('nom', 'email', 'sujet', 'date', 'traite')
    search_fields = ('nom', 'email', 'sujet')
    list_filter = ('date', 'traite')
    list_editable = ('traite',)
    date_hierarchy = 'date'

# Admin des services
class ServiceAdmin(CustomAdminCSS, admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'image', 'ordre')
    search_fields = ('titre', 'description')
    list_editable = ('ordre',)
    list_filter = ('categorie',)

# Admin des projets
class ProjetAdmin(CustomAdminCSS, admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'client', 'date', 'en_avant', 'image_preview')
    search_fields = ('titre', 'description', 'client')
    list_filter = ('categorie', 'date', 'en_avant')
    list_editable = ('en_avant',)
    date_hierarchy = 'date'
    prepopulated_fields = {'slug': ('titre',)}
    
    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image'

# Admin des articles
class ArticleAdmin(CustomAdminCSS, admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'date_publication', 'is_new', 'reading_time')
    search_fields = ('titre', 'contenu', 'tags')
    list_filter = ('date_publication', 'auteur', 'en_avant')
    prepopulated_fields = {'slug': ('titre',)}
    date_hierarchy = 'date_publication'
    
    def is_new(self, obj):
        return obj.is_new
    is_new.boolean = True
    is_new.short_description = 'Nouveau?'
    
    def reading_time(self, obj):
        return f"{obj.reading_time} min"
    reading_time.short_description = 'Temps de lecture'

# Admin des clients
class ClientAdmin(CustomAdminCSS, admin.ModelAdmin):
    list_display = ('entreprise', 'user', 'email', 'telephone', 'date_inscription')
    search_fields = ('entreprise', 'user__username', 'email')
    list_filter = ('date_inscription',)

# Admin des fichiers partagés
class FichierPartageAdmin(CustomAdminCSS, admin.ModelAdmin):
    list_display = ('titre', 'client', 'date_ajout', 'fichier_link')
    search_fields = ('titre', 'description', 'client__entreprise')
    date_hierarchy = 'date_ajout'
    
    def fichier_link(self, obj):
        from django.utils.html import format_html
        if obj.fichier:
            return format_html('<a href="{}" download>Télécharger</a>', obj.fichier.url)
        return "-"
    fichier_link.short_description = 'Fichier'

# Admin de la page d'accueil
class MessageAccueilAdmin(CustomAdminCSS, admin.ModelAdmin):
    list_display = ('titre', 'actif', 'media_preview')
    list_editable = ('actif',)
    
    def media_preview(self, obj):
        from django.utils.html import format_html
        if obj.media:
            if obj.media.url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return format_html('<img src="{}" style="max-height: 50px;" />', obj.media.url)
            else:
                return format_html('<a href="{}">Fichier média</a>', obj.media.url)
        return "-"
    media_preview.short_description = 'Média'

class InfoAdmin(admin.ModelAdmin):
    list_display = ('nom', 'bio', 'photo', 'lien_linkedin', 'lien_twitter', 'lien_github', 'lien_website', 'lien_email', 'lien_telephone', 'lien_facebook', 'lien_instagram', 'lien_youtube', 'lien_tiktok')
    search_fields = ('nom', 'bio')
    list_filter = ('lien_linkedin', 'lien_twitter', 'lien_github', 'lien_website', 'lien_email', 'lien_telephone', 'lien_facebook', 'lien_instagram', 'lien_youtube', 'lien_tiktok')
    
    
# Enregistrement des modèles avec les classes admin personnalisées
admin_site.register(TeamMember, TeamMemberAdmin)
admin_site.register(ContactMessage, ContactMessageAdmin)
admin_site.register(Service, ServiceAdmin)
admin_site.register(Projet, ProjetAdmin)
admin_site.register(Article, ArticleAdmin)
admin_site.register(Client, ClientAdmin)
admin_site.register(FichierPartage, FichierPartageAdmin)
admin_site.register(MessageAccueil, MessageAccueilAdmin)
admin_site.register(Info, InfoAdmin)

# Remplacez l'admin par défaut
admin.site = admin_site