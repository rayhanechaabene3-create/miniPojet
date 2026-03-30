from django.urls import path
from . import views
urlpatterns = [
 path('', views.index, name='index'),
 path('base/', views.base, name='base'),
 path('navbar/', views.navbar, name='navbar'),
 path('detail/<int:product_id>/', views.detail_produit, name='detail_produit'),
 
 ]  