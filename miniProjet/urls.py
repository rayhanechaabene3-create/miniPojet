from django.urls import path
from . import views  # pyrefly: ignore [missing-import]

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('inscription/', views.DonneurInscriptionView.as_view(), name='inscription'),
    path('hopital_inscription/', views.HopitalInscriptionView.as_view(), name='hopital_inscription'),
    path('connexion/', views.CustomLoginView.as_view(), name='connexion'),
    path('deconnexion/', views.CustomLogoutView.as_view(), name='deconnexion'),
    
    path('profil/modifier/', views.EditProfileView.as_view(), name='edit_profile'),
    path('profil/supprimer/', views.AccountDeleteView.as_view(), name='delete_account'),
    path('donneur/toggle_activation/', views.ToggleActivationDonneurView.as_view(), name='toggle_activation_donneur'),
    
    path('dashboard/admin/', views.AdminDashboardView.as_view(), name='dashboard_admin'),
    path('dashboard/admin/valider_hopital/<int:hopital_id>/', views.ValiderHopitalView.as_view(), name='valider_hopital'),
    path('dashboard/admin/export_donneurs/', views.ExportDonneursCSVView.as_view(), name='export_donneurs_csv'),
    path('campagnes/', views.CampagneListView.as_view(), name='list_campagnes'),
    path('campagnes/<int:campagne_id>/inscrire/', views.InscrireCampagneView.as_view(), name='inscrire_campagne'),

    # Hospital Space
    path('dashboard/hopital/', views.HopitalDashboardView.as_view(), name='dashboard_hopital'),
    path('hopital/demandes/creer/', views.DemandeCreateView.as_view(), name='create_demande'),
    path('hopital/demandes/<int:demande_id>/modifier/', views.DemandeUpdateView.as_view(), name='edit_demande'),
    path('hopital/demandes/<int:demande_id>/cloturer/', views.DemandeCloseView.as_view(), name='close_demande'),
    path('hopital/demandes/<int:demande_id>/reponses/', views.DemandeReponsesView.as_view(), name='view_reponses_demande'),
    path('hopital/reponses/<int:reponse_id>/notifier/', views.EnvoyerNotificationView.as_view(), name='envoyer_notification'),
    path('hopital/analyses/<int:analyse_id>/<str:decision>/', views.DeciderAnalyseView.as_view(), name='decider_analyse'),
    path('hopital/campagnes/creer/', views.CampagneCreateView.as_view(), name='create_campagne'),
    path('hopital/dons/<int:don_id>/valider/', views.ValiderDonView.as_view(), name='valider_don'),

    # Donor Space
    path('dashboard/donneur/', views.DonneurDashboardView.as_view(), name='dashboard_donneur'),
    path('donneur/chatbot/', views.chatbot_view, name='chatbot'),
    path('donneur/demandes/<int:demande_id>/repondre/', views.RepondreDemandeView.as_view(), name='repondre_demande'),
    path('donneur/don/enregistrer/', views.DonCreateView.as_view(), name='enregistrer_don'),
    path('donneur/analyse/envoyer/<int:notification_id>/', views.EnvoyerAnalyseView.as_view(), name='envoyer_analyse'),
]