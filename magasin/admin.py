from django.contrib import admin
from .models import Produit
from .models import Category
from .models import Fournisseur
from.models import ProduitNC
admin.site.register(Produit)
admin.site.register(Category)
admin.site.register(Fournisseur)
admin.site.register(ProduitNC)

# Register your models here.
