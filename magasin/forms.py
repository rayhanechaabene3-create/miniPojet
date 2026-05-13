from django import forms
from .models import Produit, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['libelle', 'description', 'prix', 'type', 'categorie', 'Fournisseur', 'image', 'quantite', 'solde']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prix': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'Fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'solde': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'placeholder': '0'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la catégorie'}),
        }
