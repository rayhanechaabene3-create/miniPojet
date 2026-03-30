from django.db import models
from datetime import date
class Category(models.Model):
  
  TYPE_CHOICES=[ ('Al','Alimentaire'), 
                  ('Mb','Meuble'),
                  ('Sn','Sanitaire'),
                  ('Vs','Vaisselle'),
                  ('Vt','Vêtement'),
                  ('Jx','Jouets'),
                 ('Lg','Linge de Maison'),
                 ('Bj','Bijoux'),
                 ('Dc','Décor')]
           
  name=models.CharField(max_length=50,default='Al',choices=TYPE_CHOICES)
  def __str__(self):
     return f"category : {self.name},  {self.TYPE_CHOICES} "
   

class Produit(models.Model):
    libelle = models.CharField(max_length=100)
    description = models.TextField(default='')
    prix= models.DecimalField(max_digits=10,decimal_places=3)
    TYPE_CHOICES=[ ('em','emballe'),
                 ('fr','Frais'),
                 ('cs','Conserve')
                 ]
    
         
    type= models.CharField(max_length=100)
    categorie=models.ForeignKey(Category,on_delete=models.CASCADE,null=True)
    Fournisseur=models.ForeignKey('Fournisseur',on_delete=models.CASCADE,null=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    
    
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
    dateCde = models.DateField(null=True, default=date.today)
    totalCde = models.DecimalField(max_digits=10, decimal_places=3, default=0, editable=True)

    def __str__(self):
        return f"Commande du {self.dateCde} - Total: {self.totalCde}€"