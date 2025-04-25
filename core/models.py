from django.db import models
from django.contrib.auth.models import User

# Membres de l’équipe
class TeamMember(models.Model):
    nom = models.CharField(max_length=100)
    poste = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='equipe/')
    bio = models.TextField()

    def __str__(self):
        return self.nom

# Message et média d’accueil
class MessageAccueil(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    media = models.FileField(upload_to='accueil/', blank=True, null=True)

    def __str__(self):
        return self.titre

# Messages reçus via le formulaire de contact
class ContactMessage(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    sujet = models.CharField(max_length=150)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.sujet}"

# Services proposés par l’agence
class Service(models.Model):
    CATEGORIES = [
        ('visuelle', 'Communication Visuelle'),
        ('digitale', 'Communication Digitale'),
        ('audiovisuelle', 'Audiovisuelle'),
        ('evenementielle', 'Événementielle'),
    ]
    
    titre = models.CharField(max_length=100)
    description = models.TextField()
    icone = models.CharField(max_length=50)
    categorie = models.CharField(max_length=30, choices=CATEGORIES)

    def __str__(self):
        return self.titre

# Projets du portfolio
class Projet(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio/images/')
    video = models.FileField(upload_to='portfolio/videos/', blank=True, null=True)
    date = models.DateField()
    resultat = models.TextField(blank=True)
    lien = models.URLField(blank=True)
    categorie = models.CharField(max_length=100)

    def __str__(self):
        return self.titre

# Articles de blog
class Article(models.Model):
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    contenu = models.TextField()
    auteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_publication = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to='blog/', blank=True)
    tags = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.titre

# Espace client
class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    entreprise = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.entreprise

class FichierPartagé(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    titre = models.CharField(max_length=100)
    fichier = models.FileField(upload_to='clients/fichiers/')
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

