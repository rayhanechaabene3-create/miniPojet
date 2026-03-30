from django import forms
from django.contrib.auth.models import User
from .models import Donneur, Hopital, DemandeUrgente, Don, Campagne, Inscription

GROUPE_SANGUIN_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-')
]

SEXE_CHOICES = [('M', 'Masculin'), ('F', 'Féminin')]

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Mot de passe"
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        labels = {
            'username': "Nom d'utilisateur",
            'email': "Email",
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = '' 

class DonneurRegistrationForm(forms.ModelForm):
    groupe_sanguin = forms.ChoiceField(choices=GROUPE_SANGUIN_CHOICES)
    sexe = forms.ChoiceField(choices=SEXE_CHOICES)
    
    class Meta:
        model = Donneur
        fields = ['groupe_sanguin', 'sexe', 'date_naissance', 'ville']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'groupe_sanguin': forms.Select(attrs={'class': 'form-select'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
        }

class HopitalRegistrationForm(forms.ModelForm):
    class Meta:
        model = Hopital
        fields = ['nom', 'adresse', 'ville', 'agrement']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'agrement': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DonneurProfileForm(forms.ModelForm):
    groupe_sanguin = forms.ChoiceField(choices=GROUPE_SANGUIN_CHOICES)

    class Meta:
        model = Donneur
        fields = ['groupe_sanguin', 'ville', 'actif']
        widgets = {
            'groupe_sanguin': forms.Select(attrs={'class': 'form-select'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DemandeUrgenteForm(forms.ModelForm):
    groupe_sanguin = forms.ChoiceField(choices=GROUPE_SANGUIN_CHOICES)
    
    class Meta:
        model = DemandeUrgente
        fields = ['groupe_sanguin', 'quantite', 'delai', 'description']
        widgets = {
            'groupe_sanguin': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'delai': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DonForm(forms.ModelForm):
    class Meta:
        model = Don
        fields = ['hopital', 'notes']
        widgets = {
            'hopital': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CampagneForm(forms.ModelForm):
    class Meta:
        model = Campagne
        fields = ['nom', 'date', 'lieu', 'groupes_cibles', 'capacite_totale']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'groupes_cibles': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: A+, B-, O+'}),
            'capacite_totale': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['creneau_horaire']
        widgets = {
            'creneau_horaire': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }