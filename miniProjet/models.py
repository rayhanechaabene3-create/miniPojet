from django.db import models
from django.contrib.auth.models import User

# --- Profils Utilisateurs ---

class Donneur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    groupe_sanguin = models.CharField(max_length=5)
    sexe = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin')])
    date_naissance = models.DateField()
    ville = models.CharField(max_length=100)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.groupe_sanguin})"

class Hopital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    agrement = models.CharField(max_length=100)
    valide = models.BooleanField(default=False)

    def __str__(self):
        return self.nom

# --- Gestion des Demandes et Campagnes ---
class DemandeUrgente(models.Model):
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE)
    groupe_sanguin = models.CharField(max_length=5)
    quantite = models.PositiveIntegerField()
    delai = models.DateTimeField()
    statut = models.CharField(max_length=50, default='En attente')
    description = models.TextField(blank=True)

class Campagne(models.Model):
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE)
    nom = models.CharField(max_length=200)
    date = models.DateField()
    lieu = models.CharField(max_length=255)
    groupes_cibles = models.CharField(max_length=100) # Ex: "A+, B-, O+"
    capacite_totale = models.PositiveIntegerField()

# --- Interactions et Suivi ---

class Don(models.Model):
    donneur = models.ForeignKey(Donneur, on_delete=models.CASCADE)
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE)
    date_don = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    valide = models.BooleanField(default=False)

class Inscription(models.Model):
    campagne = models.ForeignKey(Campagne, on_delete=models.CASCADE)
    donneur = models.ForeignKey(Donneur, on_delete=models.CASCADE)
    creneau_horaire = models.TimeField()
    date_inscription = models.DateTimeField(auto_now_add=True)
    present = models.BooleanField(default=False)

class ReponseAppel(models.Model):
    demande_urgente = models.ForeignKey(DemandeUrgente, on_delete=models.CASCADE)
    donneur = models.ForeignKey(Donneur, on_delete=models.CASCADE)
    date_reponse = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50) # Ex: Accepté, Décliné

class Notification(models.Model):
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    expediteur = models.ForeignKey(Hopital, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications_envoyees')
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification pour {self.destinataire.username} - {'Lu' if self.lu else 'Non lu'}"

class Analyse(models.Model):
    STATUT_CHOICES = [('en_attente', 'En attente'), ('acceptee', 'Acceptée'), ('refusee', 'Refusée')]
    donneur = models.ForeignKey(Donneur, on_delete=models.CASCADE, related_name='analyses')
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, related_name='analyses_recues')
    notification = models.ForeignKey(Notification, on_delete=models.SET_NULL, null=True, blank=True, related_name='analyses')
    fichier = models.FileField(upload_to='analyses/')
    commentaire = models.TextField(blank=True)
    date_envoi = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    def __str__(self):
        return f"Analyse de {self.donneur} pour {self.hopital}"
