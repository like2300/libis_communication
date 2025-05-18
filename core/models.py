from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
import uuid 
from django.contrib import admin
from .models import *
from django.db.models import Q


class User(AbstractUser):
    """Modèle utilisateur personnalisé"""
    is_client = models.BooleanField(
        _('client status'),
        default=False,
        help_text=_('Designates whether the user is a client.')
    )
    email_verified = models.BooleanField(
        _('email verified'),
        default=False,
        help_text=_('Designates whether the user has verified their email address.')
    )
    verification_uuid = models.UUIDField(
        _('verification UUID'),
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    profile_complete = models.BooleanField(
        _('profile complete'),
        default=False
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.email = self.email.lower()  # Normalisation de l'email
        super().save(*args, **kwargs)

class Client(models.Model):
    """Modèle pour les clients"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,  # Ceci garantit l'unicité
        verbose_name=_('user account')
    ) 
    entreprise = models.CharField(
        _('company'),
        max_length=100,
        help_text=_('The name of the company.')
    )
    profile_complete = models.BooleanField(
        _('profile complete'),
        default=False
    )
    telephone = models.CharField(
        _('phone number'),
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        help_text=_('Phone number in international format.')
    )
    secteur_activite = models.CharField(
        _('activity sector'), 
        max_length=100,
        blank=True,
        null=True
    )
    adresse = models.TextField(
        _('address'),
        blank=True,
        null=True
    )
    date_inscription = models.DateTimeField(
        _('signup date'),
        auto_now_add=True
    ) 
    @classmethod
    def search(cls, query):
        return cls.objects.filter(
            Q(entreprise__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query)
        )
    class Meta:
        verbose_name = _('Client')
        verbose_name_plural = _('Clients')
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.entreprise} ({self.user.email})"

    def clean(self):
        if not hasattr(self, 'user') or not self.user.is_authenticated:
            raise ValidationError(_("User must be authenticated"))
    
    @property
    def nom_complet(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    @property
    def email(self):
        """Récupère l'email depuis le modèle User"""
        return self.user.email

    def save(self, *args, **kwargs):
        self.user.is_client = True
        self.user.save()
        super().save(*args, **kwargs)

class Projet(models.Model):
    """Modèle pour les projets portfolio"""
    CATEGORIE_CHOICES = [
        ('visuelle', _('Visual Communication')),
        ('digitale', _('Digital Communication')),
        ('audiovisuelle', _('Audiovisual')),
        ('evenementielle', _('Event')),
    ]
    
    titre = models.CharField(
        _('title'),
        max_length=200
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True
    )
    description = models.TextField(
        _('description')
    )
    image = models.ImageField(
        _('image'),
        upload_to='portfolio/images/'
    )
    video = models.FileField(
        _('video'),
        upload_to='portfolio/videos/',
        blank=True,
        null=True
    )
    date = models.DateField(
        _('project date')
    )
    resultat = models.TextField(
        _('result'),
        blank=True,
        null=True
    )
    categorie = models.CharField(
        _('category'),
        max_length=100,
        choices=CATEGORIE_CHOICES
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        verbose_name=_('client'),
        null=True,
        blank=True
    )
    lien = models.URLField(
        _('link'),
        blank=True,
        null=True
    )
    en_avant = models.BooleanField(
        _('featured'),
        default=False
    )
    services = models.ManyToManyField(
        'Service',
        blank=True,
        verbose_name=_('services')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def search(cls, query):
        return cls.objects.filter(
            Q(titre__icontains=query) |
            Q(description__icontains=query) |
            Q(client__entreprise__icontains=query)
        )

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['slug'],
                name='unique_project_slug'
            )
        ]

    def __str__(self):
        return self.titre
    
    def clean(self):
        if self.en_avant and Projet.objects.filter(en_avant=True).exclude(id=self.id).count() >= 3:
            raise ValidationError(_("Only 3 projects can be featured"))
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('projet_detail', args=[self.id, self.slug])

class Service(models.Model):
    """Modèle pour les services offerts"""
    CATEGORIES = [
        ('visuelle', 'Communication Visuelle'),
        ('digitale', 'Communication Digitale'),
        ('audiovisuelle', 'Audiovisuelle'),
        ('evenementielle', 'Événementielle'),
    ]
    
    titre = models.CharField(
        _('title'),
        max_length=100
    )
    description = models.TextField(
        _('description')
    )
    image = models.ImageField(
        upload_to='services/images/',
        null=True,
        blank=True
    )
    categorie = models.CharField(
        _('category'),
        max_length=30,
        choices=CATEGORIES
    )
    ordre = models.PositiveIntegerField(
        _('order'),
        default=0
    )
    slug = models.SlugField(
        unique=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ['ordre']

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

class TeamMember(models.Model):
    """Modèle pour les membres de l'équipe"""
    nom = models.CharField(
        _('name'),
        max_length=100
    )
    poste = models.CharField(
        _('position'),
        max_length=100
    )
    photo = models.ImageField(
        upload_to='team/'
    )
    bio = models.TextField(
        _('biography')
    )
    competences = models.CharField(
        _('skills'),
        max_length=255,
        blank=True,
        null=True
    )
    lien_linkedin = models.URLField(
        blank=True,
        null=True
    )
    lien_twitter = models.URLField(
        blank=True,
        null=True
    )

    @classmethod
    def search(cls, query):
        return cls.objects.filter(
            Q(nom__icontains=query) |
            Q(poste__icontains=query) |
            Q(bio__icontains=query) |
            Q(competences__icontains=query)
        )
    
    class Meta:
        verbose_name = _("Team Member")
        verbose_name_plural = _("Team Members")
        ordering = ['nom']

    def __str__(self):
        return self.nom

    @property
    def competences_list(self):
        return [c.strip() for c in self.competences.split(',')] if self.competences else []
    
    def get_absolute_url(self):
        return reverse('team_member_detail', args=[self.id])

class Article(models.Model):
    """Modèle pour les articles de blog"""
    titre = models.CharField(
        _('title'),
        max_length=200
    )
    slug = models.SlugField(
        unique=True
    )
    contenu = models.TextField(
        _('content')
    )
    auteur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name=_('author'),
        null=True,
        blank=True
    )
    date_publication = models.DateField(
        _('publication date'),
        auto_now_add=True
    )
    image = models.ImageField(
        upload_to='blog/'
    )
    tags = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    en_avant = models.BooleanField(
        _('featured'),
        default=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ['-date_publication']

    def __str__(self):
        return self.titre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)
    
    @property
    def is_new(self):
        return (timezone.now().date() - self.date_publication).days < 7
    
    @property
    def reading_time(self):
        word_count = len(self.contenu.split())
        return max(1, round(word_count / 180))
    
    def get_absolute_url(self):
        return reverse('article_detail', args=[self.slug])

class ContactMessage(models.Model):
    nom = models.CharField(_('name'), max_length=100)
    email = models.EmailField()
    sujet = models.CharField(_('subject'), max_length=150)
    message = models.TextField()
    date = models.DateTimeField(_('date received'), auto_now_add=True)
    traite = models.BooleanField(_('processed'), default=False)
    is_read = models.BooleanField(_('read'), default=False)

    @classmethod
    def search(cls, query):
        return cls.objects.filter(
            Q(nom__icontains=query) |
            Q(email__icontains=query) |
            Q(sujet__icontains=query) |
            Q(message__icontains=query)
        )
    class Meta:
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
        ordering = ['-date']
        permissions = [
            ('can_view_all_messages', _('Can view all messages')),
            ('can_export_messages', _('Can export messages')),
        ]

    def __str__(self):
        return f"{self.nom} - {self.sujet}"

    def save(self, *args, **kwargs):
        """Automatically mark as read when processed"""
        if self.traite and not self.is_read:
            self.is_read = True
        super().save(*args, **kwargs)
    
    @admin.display(boolean=True, description='Status')
    def status(self):
        if self.traite:
            return _("Processed")
        return _("Read") if self.is_read else _("Unread")
    
    @property
    def is_recent(self):
        return self.date >= timezone.now() - timezone.timedelta(days=7)

class Info(models.Model):
    """Modèle pour les informations de l'entreprise"""
    nom = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='info/')
    lien_linkedin = models.URLField(blank=True)
    lien_twitter = models.URLField(blank=True)
    lien_github = models.URLField(blank=True)
    lien_website = models.URLField(blank=True)
    lien_email = models.EmailField(blank=True)
    lien_telephone = models.CharField(max_length=20, blank=True)
    lien_facebook = models.URLField(blank=True)
    lien_instagram = models.URLField(blank=True)
    lien_youtube = models.URLField(blank=True)
    lien_tiktok = models.URLField(blank=True)

    class Meta:
        verbose_name = "Information"
        verbose_name_plural = "Informations"

    def __str__(self):
        return self.nom

# core/models.py
 
class ContactMessage(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    sujet = models.CharField(max_length=150)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False)
    
    # Add this if you want is_read functionality
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.nom} - {self.sujet}"

class MessageAccueil(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    media = models.FileField(upload_to='accueil/', blank=True, null=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.titre

    class Meta:
        verbose_name = "Message d'accueil"
        verbose_name_plural = "Messages d'accueil"

class Projets_user(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='fichiers')
    titre = models.CharField(max_length=100)
    # fille is img fichier = models.ImageField(upload_to='clients/fichiers/', blank=True, null=True)
    fichier = models.FileField(upload_to='clients/fichiers/', blank=True, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)  # This is your date field
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='clients/images/', blank=True, null=True)
    video = models.FileField(upload_to='clients/videos/', blank=True, null=True)
    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)   
    status = models.BooleanField(
        _('status'),
        default=False,
        help_text=_('status project.')
    )
   
    # Champ slug (facultatif : rempli automatiquement)
    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = _("Projets_user")
        verbose_name_plural = _("Projets_user")
        ordering = ['-date_ajout']

    def __str__(self):
        return self.titre