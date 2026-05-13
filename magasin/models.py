from django.db import models
from django.contrib.auth.models import User
from datetime import date
from decimal import Decimal
class Category(models.Model):
  name = models.CharField(max_length=50)

  def __str__(self):
     return self.name
   

class Produit(models.Model):
    libelle = models.CharField(max_length=100)
    description = models.TextField(default='')
    prix = models.DecimalField(max_digits=10,decimal_places=3)
    TYPE_CHOICES = [
        ('em', 'emballe'),
        ('fr', 'Frais'),
        ('cs', 'Conserve')
    ]

    type = models.CharField(max_length=100, choices=TYPE_CHOICES, default='em')
    categorie = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    Fournisseur = models.ForeignKey('Fournisseur', on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    quantite = models.PositiveIntegerField(default=0)
    solde = models.PositiveIntegerField(default=0, help_text='Remise en % (0 = pas de solde)')

    @property
    def prix_final(self):
        if self.solde and self.solde > 0:
            return round(self.prix * (1 - Decimal(self.solde) / Decimal(100)), 3)
        return self.prix
    
    
    def __str__(self):
      return f"Produit : {self.libelle}, {self.description}, {self.prix} DT, {self.type} "
    
    
class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.TextField()
    email = models.EmailField()
    telephone = models.CharField(max_length=8)
    
    def __str__(self):
        return f"Fournisseur : {self.nom}, {self.adresse}, {self.email}, {self.telephone}"
   
# Sous-classe : Produit Non Consommable
class ProduitNC(Produit):
    duree_garantie = models.CharField(max_length=100)

    def __str__(self):
        return f"Produit Non Consommable : {self.libelle}, {self.description}, {self.prix} DT, {self.type}, Durée de Garantie: {self.duree_garantie}"
class Commande(models.Model):
    client = models.CharField(max_length=150, default='')
    nom = models.CharField(max_length=150, default='')
    email = models.EmailField(default='')
    telephone = models.CharField(max_length=20, default='')
    adresse = models.TextField(default='')
    dateCde = models.DateField(null=True, default=date.today)
    totalCde = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    def __str__(self):
        return f"Commande #{self.id} — {self.client} — {self.dateCde}"

class CommandeItem(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='items')
    produit_nom = models.CharField(max_length=100)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=3)

    def total(self):
        return round(self.quantite * self.prix_unitaire, 3)

class Favori(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoris')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='favoris')

    class Meta:
        unique_together = ('user', 'produit')

    def __str__(self):
        return f"{self.user.username} ♥ {self.produit.libelle}"