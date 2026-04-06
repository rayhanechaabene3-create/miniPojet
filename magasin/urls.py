from django.urls import path
from . import views

urlpatterns = [
    path('', views.inde, name='inde'),
    path('categorie/<int:category_id>/', views.category_products, name='category_products'),
    path('base/', views.base, name='base'),
    path('navbar/', views.navbar, name='navbar'),
    path('detail/<int:product_id>/', views.detail_produit, name='detail_produit'),
    path('panier/', views.panier, name='panier'),
    path('panier/ajouter/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add_to_cart_with_quantity/<int:product_id>/', views.add_to_cart_with_quantity, name='add_to_cart_with_quantity'),
    path('panier/update/<str:product_id>/', views.update_cart, name='update_cart'),
    path('panier/remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),
]