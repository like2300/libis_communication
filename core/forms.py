from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from django.contrib.auth.forms import ( 
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
    PasswordChangeForm
)
from django.conf import settings
from .models import *  
from django.urls import reverse_lazy 
from django.forms import ModelForm 



User = get_user_model()

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Choose a username')
        }),
        help_text=_("150 characters max. Letters, digits and @/./+/-/_ only.")
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your email address')
        }),
        required=True
    )
 

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("This email is already registered."))
        return email
 
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.is_active = False
        user.email_verified = False  # Assure que ce champ existe

        if commit:
            user.save()

            
        return user



class LoginForm(forms.Form):
    username = forms.CharField(
        label=_("Nom d'utilisateur ou email"),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get("username")
        password = cleaned_data.get("password")

        # Trouver l'utilisateur par email ou username
        user = User.objects.filter(email__iexact=username_or_email).first()
        if not user:
            user = User.objects.filter(username=username_or_email).first()

        if not user:
            raise ValidationError(_("Aucun compte ne correspond à cet identifiant."))

        # Authentifier
        authenticated_user = authenticate(username=user.username, password=password)
        if authenticated_user is None:
            raise ValidationError(_("Mot de passe incorrect."))

        # Stocker l'utilisateur authentifié pour y accéder ailleurs si besoin
        self.user = authenticated_user

        return cleaned_data


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Email'),
            'autocomplete': 'email'
        })
    )

    def get_users(self, email):
        """Override to use custom user model and case-insensitive email lookup"""
        active_users = User._default_manager.filter(
            email__iexact=email,
            is_active=True,
            email_verified=True  # Only allow password reset for verified emails
        )
        return (u for u in active_users if u.has_usable_password())


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('New password'),
            'autocomplete': 'new-password'
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm new password'),
            'autocomplete': 'new-password'
        }),
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_("Current password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Current password'),
            'autocomplete': 'current-password'
        }),
    )
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('New password'),
            'autocomplete': 'new-password'
        }),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm new password'),
            'autocomplete': 'new-password'
        }),
    )


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['entreprise', 'telephone', 'secteur_activite', 'adresse']
        widgets = {
            'entreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'secteur_activite': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }



from django import forms
from django.utils.translation import gettext_lazy as _

class ContactForm(forms.Form):
    nom = forms.CharField(
        label=_("Nom"),
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Votre nom complet')
        })
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Votre adresse email')
        })
    )
    sujet = forms.CharField(
        label=_("Sujet"),
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Sujet de votre message')
        })
    )
    message = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': _('Tapez votre message ici...'),
            'rows': 5
        })
    )





class UserEditForm(forms.ModelForm):
    """Formulaire d'édition pour les informations de base de l'utilisateur"""
    class Meta:
        model = User
        fields = [ 'email']
        widgets = {
             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse email'}),
        }



class ClientEditForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['entreprise', 'telephone', 'secteur_activite', 'adresse']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'entreprise': _('Company'),
            'telephone': _('Phone number'),
            'secteur_activite': _('Activity sector'),
            'adresse': _('Address'),
        }

# admin form
class ProjetForm(forms.ModelForm):
    """Formulaire d'édition pour les informations de base de l'utilisateur"""
    class Meta:
        model = Projet
        fields = ['titre', 'description', 'categorie', 'client', 'date', 'image', 'video', 'lien']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}) ,
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'video': forms.TextInput(attrs={'class': 'form-control'}),
            'lien': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'titre': _('Title'),
            'description': _('Description'),
            'categorie': _('Category'),
            'client': _('Client '),
            'date': _('Date'),
            'image': _('Image'),
            'video': _('Video URL'),
            'lien': _('Link'),
        }


# client form
class Projets_userForms(forms.ModelForm):
    class Meta:
        model = Projets_user
        fields = ['titre', 'description', 'fichier', 'image', 'video', 'date_debut', 'date_fin']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Titre du projet')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Description détaillée')
            }),
            'date_debut': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'titre': _('Titre'),
            'description': _('Description'),
            'fichier': _('Fichier principal'),
            'image': _('Image'),
            'video': _('Vidéo'),
            'date_debut': _('Date de début'),
            'date_fin': _('Date de fin'),
        }
        help_texts = {
            'fichier': _('Téléversez le fichier principal du projet'),
            'video': _('Formats supportés: MP4, AVI, MOV'),
        }

    def __init__(self, *args, **kwargs):
        self.client = kwargs.pop('client', None)
        super().__init__(*args, **kwargs)
        self.fields['fichier'].required = True
        self.fields['fichier'].widget.attrs.update({
            'class': 'form-control-file',
            'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.rar'
        })
        self.fields['image'].widget.attrs.update({
            'class': 'form-control-file',
            'accept': 'image/*'
        })
        self.fields['video'].widget.attrs.update({
            'class': 'form-control-file',
            'accept': 'video/*'
        })

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')

        if date_debut and date_fin and date_fin < date_debut:
            self.add_error('date_fin', _('La date de fin doit être postérieure à la date de début'))

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.client:
            instance.client = self.client
        if commit:
            instance.save()
        return instance
 





# Formulaire pour créer/modifier un client
class AdminClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['entreprise', 'telephone', 'secteur_activite', 'adresse']
        widgets = {
            'entreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'secteur_activite': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

# Formulaire pour créer/modifier un projet
class AdminProjectForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ['titre', 'description', 'categorie', 'client', 'date', 'image', 'video', 'lien', 'en_avant']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'video': forms.URLInput(attrs={'class': 'form-control'}),
            'lien': forms.URLInput(attrs={'class': 'form-control'}),
            'en_avant': forms.CheckboxInput(),
        }

# Formulaire pour éditer ou créer un membre d'équipe
class AdminTeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['nom', 'poste', 'bio', 'photo', 'competences', 'lien_linkedin', 'lien_twitter']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'poste': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'competences': forms.TextInput(attrs={'class': 'form-control'}),
            'lien_linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'lien_twitter': forms.URLInput(attrs={'class': 'form-control'}),
        }

# Formulaire pour répondre à un message
class AdminMessageReplyForm(forms.Form):
    reply_message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        label="Réponse"
    )





 
class MessageForm(forms.Form):
    destinataire = forms.EmailField(
        label=_("Destinataire"),
        help_text=_("L'adresse email du destinataire")
    )
    sujet = forms.CharField(
        label=_("Sujet"),
        max_length=150
    )
    message = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea
    )

