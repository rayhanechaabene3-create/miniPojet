from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('inscription/', views.inscription, name='inscription'),
    path('hopital_inscription/', views.hopital_inscription, name='hopital_inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    
    path('profil/modifier/', views.edit_profile, name='edit_profile'),
    path('profil/supprimer/', views.delete_account, name='delete_account'),
    path('donneur/toggle_activation/', views.toggle_activation_donneur, name='toggle_activation_donneur'),
    
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/admin/valider_hopital/<int:hopital_id>/', views.valider_hopital, name='valider_hopital'),
    path('dashboard/admin/export_donneurs/', views.export_donneurs_csv, name='export_donneurs_csv'),
    path('campagnes/', views.list_campagnes, name='list_campagnes'),
    path('campagnes/<int:campagne_id>/inscrire/', views.inscrire_campagne, name='inscrire_campagne'),

    # Hospital Space
    path('dashboard/hopital/', views.dashboard_hopital, name='dashboard_hopital'),
    path('hopital/demandes/creer/', views.create_demande, name='create_demande'),
    path('hopital/demandes/<int:demande_id>/modifier/', views.edit_demande, name='edit_demande'),
    path('hopital/demandes/<int:demande_id>/cloturer/', views.close_demande, name='close_demande'),
    path('hopital/demandes/<int:demande_id>/reponses/', views.view_reponses_demande, name='view_reponses_demande'),
    path('hopital/campagnes/creer/', views.create_campagne, name='create_campagne'),

    # Donor Space
    path('dashboard/donneur/', views.dashboard_donneur, name='dashboard_donneur'),
    path('donneur/demandes/<int:demande_id>/repondre/', views.repondre_demande, name='repondre_demande'),
    path('donneur/don/enregistrer/', views.enregistrer_don, name='enregistrer_don'),
]