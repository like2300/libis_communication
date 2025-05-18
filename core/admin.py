from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

from django.utils.translation import gettext_lazy as _



class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 
                    'is_staff', 'is_client', 'email_verified')
    list_filter = ('is_staff', 'is_superuser', 'is_client', 'email_verified')
    readonly_fields = ('verification_uuid',)  # <-- Ajout ici

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 
                       'is_client', 'email_verified', 'groups', 
                       'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Verification'), {'fields': ('verification_uuid',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

class ClientAdmin(admin.ModelAdmin):
    list_display = ('entreprise',  'email', 'telephone', 'profile_complete',
                   'secteur_activite', 'date_inscription')
    list_filter = ('secteur_activite', 'date_inscription')
    search_fields = ('entreprise', 'user__first_name', 'user__last_name', 
                    'user__email', 'telephone')
    raw_id_fields = ('user',)
    readonly_fields = ('date_inscription',   'email')

    fieldsets = (
        (_('User Account'), {'fields': ('user',  'email')}),
        (_('Company Information'), {
            'fields': ('entreprise', 'secteur_activite', 'telephone', 'adresse')
        }),
        (_('Dates'), {'fields': ('date_inscription',)}),
    )

class ProjetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'client', 'date', 'en_avant')
    list_filter = ('categorie', 'en_avant', 'date', 'client')
    search_fields = ('titre', 'description', 'client__entreprise')
    prepopulated_fields = {'slug': ('titre',)}
    filter_horizontal = ('services',)
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('titre', 'slug', 'description', 'categorie')
        }),
        (_('Media'), {
            'fields': ('image', 'video', 'lien')
        }),
        (_('Details'), {
            'fields': ('date', 'resultat', 'client', 'services', 'en_avant')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'ordre')
    list_filter = ('categorie',)
    search_fields = ('titre', 'description')
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('titre', 'slug', 'description', 'categorie', 'ordre')
        }),
        (_('Media'), {
            'fields': ('image',)
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('nom', 'poste', 'lien_linkedin')
    search_fields = ('nom', 'poste', 'bio')
    readonly_fields = ('competences_list',)

    fieldsets = (
        (None, {
            'fields': ('nom', 'poste', 'bio', 'photo')
        }),
        (_('Skills'), {
            'fields': ('competences', 'competences_list')
        }),
        (_('Social Links'), {
            'fields': ('lien_linkedin', 'lien_twitter'),
            'classes': ('collapse',)
        }),
    )


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'date_publication', 'en_avant', 'is_new')
    list_filter = ('en_avant', 'date_publication', 'auteur')
    search_fields = ('titre', 'contenu', 'tags')
    prepopulated_fields = {'slug': ('titre',)}
    raw_id_fields = ('auteur',)
    date_hierarchy = 'date_publication'
    readonly_fields = ('created_at', 'updated_at', 'reading_time', 'date_publication')

    fieldsets = (
        (None, {
            'fields': ('titre', 'slug', 'contenu', 'auteur')
        }),
        (_('Media'), {
            'fields': ('image', 'tags')
        }),
        (_('Publication'), {
            'fields': ('date_publication', 'en_avant'),
            'description': _('Publication date is automatically set when article is first created')
        }),
        (_('Metadata'), {
            'fields': ('reading_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_new(self, obj):
        return obj.is_new
    is_new.boolean = True
    is_new.short_description = _('New?')


# Uncomment and fix the ContactMessageAdmin class
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'sujet', 'is_read', 'traite', 'date', 'status')
    list_filter = ('is_read', 'traite', 'date')
    search_fields = ('nom', 'email', 'sujet', 'message')
    list_editable = ('is_read', 'traite')
    actions = ['mark_as_read', 'mark_as_processed', 'mark_as_unread']
    readonly_fields = ('date',)
    
    fieldsets = (
        (None, {'fields': ('nom', 'email', 'sujet', 'message')}),
        ('Status', {
            'fields': ('is_read', 'traite'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date',),
            'classes': ('collapse',)
        }),
    )
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = _("Mark selected messages as read")
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = _("Mark selected messages as unread")
    
    def mark_as_processed(self, request, queryset):
        queryset.update(traite=True)
    mark_as_processed.short_description = _("Mark selected messages as processed")
    
    def status(self, obj):
        if obj.traite:
            return _("Processed")
        return _("Read") if obj.is_read else _("Unread") 

class InfoAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Permet seulement un seul enregistrement
        return not Info.objects.exists()



class Projets_userAdmin(admin.ModelAdmin):
    list_display = ('titre', 'client', 'date_ajout', 'date_debut', 'date_fin', )
    list_filter = ('client', 'date_ajout', 'date_debut')
    search_fields = ('titre', 'description', 'client__entreprise')
    readonly_fields = ('date_ajout',)
    

    fieldsets = (
        (None, {
            'fields': ('client', 'titre', 'description')
        }),
        ('Files', {
            'fields': ('fichier', 'image', 'video')
        }),
        ('Dates', {
            'fields': ('date_ajout', 'date_debut', 'date_fin'),
            'classes': ('collapse',)
        }),
    )


 

admin.site.register(User, CustomUserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Projet, ProjetAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(Article, ArticleAdmin) 
admin.site.register(Info, InfoAdmin)
admin.site.register(MessageAccueil)
admin.site.register(Projets_user, Projets_userAdmin)