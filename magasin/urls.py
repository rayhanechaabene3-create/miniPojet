from django.urls import path, include
from rest_framework import routers
from . import views

urlpatterns = [
    path('admin-magasin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-magasin/ajouter/', views.admin_add_product, name='admin_add_product'),
    path('admin-magasin/modifier/<int:product_id>/', views.admin_edit_product, name='admin_edit_product'),
    path('admin-magasin/supprimer/<int:product_id>/', views.admin_delete_product, name='admin_delete_product'),
    path('admin-magasin/categories/ajouter/', views.admin_add_category, name='admin_add_category'),
    path('admin-magasin/categories/modifier/<int:category_id>/', views.admin_edit_category, name='admin_edit_category'),
    path('admin-magasin/categories/supprimer/<int:category_id>/', views.admin_delete_category, name='admin_delete_category'),
    path('favoris/', views.mes_favoris, name='mes_favoris'),
    path('favoris/toggle/<int:product_id>/', views.toggle_favori, name='toggle_favori'),
    path('profil/', views.profil, name='profil_magasin'),
    path('langue/', views.set_language_magasin, name='set_language_magasin'),
    path('inscription/', views.inscription_magasin, name='inscription_magasin'),
    path('connexion/', views.connexion_magasin, name='connexion_magasin'),
    path('deconnexion/', views.deconnexion_magasin, name='deconnexion_magasin'),
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

router = routers.SimpleRouter()
router.register('categorie', views.CategoryViewset, basename='categorie')
router.register('produit', views.ProduitViewset, basename='produit')

urlpatterns += [
    path('api/', include(router.urls)),
    path('api/csrf/', views.api_csrf),
    path('api/login/', views.api_login),
    path('api/logout/', views.api_logout),
    path('api/me/', views.api_me),
    path('api/inscription/', views.api_inscription),
    path('api/profil/', views.api_profil),
    path('api/commande/', views.api_commande),
    path('api/favoris/', views.api_favoris),
    path('api/commandes/', views.api_commandes_list),
]