from itertools import product

from django.shortcuts import render
from .models import Produit
from .models import Category
#from django.http import HttpResponse
def index(request):
    products = Produit.objects.all()
    return render(request,'magasin/mesProduit.html', {'products': products})
def base(request):
    return render(request,'magasin/base.html')
def navbar(request):
    products = Produit.objects.all()
    categories= Category.objects.all()
    return render(request,'magasin/navbar.html', {'products': products, 'categories': categories})
def detail_produit(request, product_id):
    product = Produit.objects.get(id=product_id)
    return render(request, 'magasin/detail.html', {'produit': product})
def add_product(request):
    return render(request, 'magasin/add.html')
def accueil(request):
    return render(request , 'accueil.html' )