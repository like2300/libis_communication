from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse

class Projet(models.Model):
    CATEGORIE_CHOICES = [
        ('visuelle', 'Communication Visuelle'),
        ('digitale', 'Communication Digitale'),
        ('audiovisuelle', 'Audiovisuelle'),
        ('evenementielle', 'Événementielle'),
    ]
    
    titre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)  # Version sécurisée
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio/images/')
    video = models.FileField(upload_to='portfolio/videos/', blank=True, null=True)
    date = models.DateField()
    resultat = models.TextField(blank=True)
    categorie = models.CharField(max_length=100, choices=CATEGORIE_CHOICES)
    client = models.CharField(max_length=100, blank=True)
    lien = models.URLField(blank=True)
    en_avant = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date']
        verbose_name = "projet"
        verbose_name_plural = "projets"
    
    def __str__(self):
        return self.titre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('projet_detail', args=[self.id, self.slug])

class TeamMember(models.Model):
    nom = models.CharField(max_length=100)
    poste = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='equipe/')
    bio = models.TextField()
    competences = models.CharField(max_length=255, blank=True)
    lien_linkedin = models.URLField(blank=True)
    lien_twitter = models.URLField(blank=True)

    def __str__(self):
        return self.nom

    @property
    def competences_list(self):
        return [c.strip() for c in self.competences.split(',')] if self.competences else []

class MessageAccueil(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    media = models.FileField(upload_to='accueil/', blank=True, null=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.titre

class ContactMessage(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    sujet = models.CharField(max_length=150)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']
        verbose_name = "message de contact"
        verbose_name_plural = "messages de contact"

    def __str__(self):
        return f"{self.nom} - {self.sujet}"

class Service(models.Model):
    CATEGORIES = [
        ('visuelle', 'Communication Visuelle'),
        ('digitale', 'Communication Digitale'),
        ('audiovisuelle', 'Audiovisuelle'),
        ('evenementielle', 'Événementielle'),
    ]
    
    titre = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='services/images/',null=True,blank=True)
    categorie = models.CharField(max_length=30, choices=CATEGORIES)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordre']
        verbose_name = "service"
        verbose_name_plural = "services"

    def __str__(self):
        return self.titre

class Article(models.Model):
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    contenu = models.TextField()
    auteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_publication = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to='blog/')
    tags = models.CharField(max_length=200, blank=True)
    en_avant = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_publication']
        verbose_name = "article"
        verbose_name_plural = "articles"

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

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    entreprise = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.entreprise

class FichierPartage(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    titre = models.CharField(max_length=100)
    fichier = models.FileField(upload_to='clients/fichiers/')
    date_ajout = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_ajout']
        verbose_name = "fichier partagé"
        verbose_name_plural = "fichiers partagés"

    def __str__(self):
        return self.titre

class Info(models.Model):
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

    def __str__(self):
        return self.nom