from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
import csv
from .forms import UserForm, DonneurRegistrationForm, HopitalRegistrationForm, DonneurProfileForm, DemandeUrgenteForm, CampagneForm, InscriptionForm
from .models import Donneur, Hopital, DemandeUrgente, Don, Campagne, ReponseAppel, Inscription

def index(request):
    return render(request, 'miniProjet/index.html')

def inscription(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        donneur_form = DonneurRegistrationForm(request.POST)
        if user_form.is_valid() and donneur_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            donneur = donneur_form.save(commit=False)
            donneur.user = user
            donneur.save()
            messages.success(request, 'Inscription réussie! Connectez-vous maintenant.')
            return redirect('connexion')
    else:
        user_form = UserForm()
        donneur_form = DonneurRegistrationForm()
    return render(request, 'miniProjet/inscription.html', {'user_form': user_form, 'donneur_form': donneur_form})

def hopital_inscription(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        hopital_form = HopitalRegistrationForm(request.POST)
        if user_form.is_valid() and hopital_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            hopital = hopital_form.save(commit=False)
            hopital.user = user
            hopital.save() # default valide=False
            messages.success(request, "Inscription hôpital réussie! Votre compte doit être validé par un administrateur.")
            return redirect('connexion')
    else:
        user_form = UserForm()
        hopital_form = HopitalRegistrationForm()
    return render(request, 'miniProjet/hopital_inscription.html', {'user_form': user_form, 'hopital_form': hopital_form})

def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('dashboard_admin')
            if hasattr(user, 'donneur'):
                return redirect('dashboard_donneur')
            if hasattr(user, 'hopital'):
                if not user.hopital.valide:
                    logout(request)
                    messages.error(request, 'Votre compte hôpital n\'est pas encore validé par l\'administrateur.')
                    return redirect('connexion')
                return redirect('dashboard_hopital')
            return redirect('index')
        else:
            messages.error(request, 'Login ou mot de passe incorrect.')
            return redirect('connexion')
    return render(request, 'miniProjet/connexion.html')

def deconnexion(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie.')
    return redirect('connexion')

@login_required
def edit_profile(request):
    if hasattr(request.user, 'donneur'):
        donneur = request.user.donneur
        if request.method == 'POST':
            form = DonneurProfileForm(request.POST, instance=donneur)
            user_form = UserForm(request.POST, instance=request.user)
            user_form.fields.pop('password') # We don't update password here
            if form.is_valid() and user_form.is_valid():
                form.save()
                user_form.save()
                messages.success(request, 'Profil mis à jour avec succès.')
                return redirect('dashboard_donneur')
        else:
            form = DonneurProfileForm(instance=donneur)
            user_form = UserForm(instance=request.user)
            user_form.fields.pop('password')
        return render(request, 'miniProjet/edit_profile_donneur.html', {'form': form, 'user_form': user_form})
    elif hasattr(request.user, 'hopital'):
        # Just simple user info update
        if request.method == 'POST':
            user_form = UserForm(request.POST, instance=request.user)
            user_form.fields.pop('password')
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Profil mis à jour avec succès.')
                return redirect('dashboard_hopital')
        else:
            user_form = UserForm(instance=request.user)
            user_form.fields.pop('password')
        return render(request, 'miniProjet/edit_profile_hopital.html', {'user_form': user_form})
    return redirect('index')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Compte supprimé avec succès.')
        return redirect('index')
    return render(request, 'miniProjet/delete_account.html')

@login_required
def toggle_activation_donneur(request):
    if hasattr(request.user, 'donneur'):
        donneur = request.user.donneur
        donneur.actif = not donneur.actif
        donneur.save()
        messages.success(request, f'Votre compte est maintenant {"actif" if donneur.actif else "inactif"}.')
        return redirect('dashboard_donneur')
    return redirect('index')

# --- HOPITAL VIEWS ---
@login_required
def dashboard_hopital(request):
    if hasattr(request.user, 'hopital'):
        demandes = DemandeUrgente.objects.filter(hopital=request.user.hopital).order_by('-delai')
        campagnes = Campagne.objects.filter(hopital=request.user.hopital).order_by('-date')
        return render(request, 'miniProjet/dashboard_hopital.html', {'demandes': demandes, 'campagnes': campagnes})
    return redirect('index')

@login_required
def create_campagne(request):
    if hasattr(request.user, 'hopital'):
        if request.user.hopital.valide:
            if request.method == 'POST':
                form = CampagneForm(request.POST)
                if form.is_valid():
                    campagne = form.save(commit=False)
                    campagne.hopital = request.user.hopital
                    campagne.save()
                    messages.success(request, 'Campagne de collecte créée avec succès.')
                    return redirect('dashboard_hopital')
            else:
                form = CampagneForm()
            return render(request, 'miniProjet/campagne_form.html', {'form': form})
        else:
            messages.error(request, "Votre compte hôpital doit être validé pour créer une campagne.")
            return redirect('dashboard_hopital')
    return redirect('index')

@login_required
def create_demande(request):
    if hasattr(request.user, 'hopital'):
        if request.method == 'POST':
            form = DemandeUrgenteForm(request.POST)
            if form.is_valid():
                demande = form.save(commit=False)
                demande.hopital = request.user.hopital
                demande.statut = 'Ouverte'
                demande.save()
                messages.success(request, 'Demande urgente publiée avec succès !')
                return redirect('dashboard_hopital')
        else:
            form = DemandeUrgenteForm()
        return render(request, 'miniProjet/demande_form.html', {'form': form, 'action': 'Créer'})
    return redirect('index')

@login_required
def edit_demande(request, demande_id):
    if hasattr(request.user, 'hopital'):
        demande = get_object_or_404(DemandeUrgente, id=demande_id, hopital=request.user.hopital)
        if request.method == 'POST':
            form = DemandeUrgenteForm(request.POST, instance=demande)
            if form.is_valid():
                form.save()
                messages.success(request, 'Demande mise à jour.')
                return redirect('dashboard_hopital')
        else:
            form = DemandeUrgenteForm(instance=demande)
        return render(request, 'miniProjet/demande_form.html', {'form': form, 'action': 'Modifier', 'demande': demande})
    return redirect('index')

@login_required
def close_demande(request, demande_id):
    if hasattr(request.user, 'hopital'):
        demande = get_object_or_404(DemandeUrgente, id=demande_id, hopital=request.user.hopital)
        demande.statut = 'Clôturée'
        demande.save()
        messages.success(request, 'La demande a été clôturée.')
        return redirect('dashboard_hopital')
    return redirect('index')

@login_required
def view_reponses_demande(request, demande_id):
    if hasattr(request.user, 'hopital'):
        demande = get_object_or_404(DemandeUrgente, id=demande_id, hopital=request.user.hopital)
        reponses = ReponseAppel.objects.filter(demande_urgente=demande).order_by('-date_reponse')
        return render(request, 'miniProjet/reponses_demande.html', {'demande': demande, 'reponses': reponses})
    return redirect('index')

from datetime import timedelta
from django.utils import timezone
from .forms import DonForm

def get_compatibilite(groupe):
    # Dictionnaire de compatibilité: clés = groupe du receveur (demande), valeurs = donneurs compatibles
    comp_map = {
        'A+': ['A+', 'A-', 'O+', 'O-'],
        'A-': ['A-', 'O-'],
        'B+': ['B+', 'B-', 'O+', 'O-'],
        'B-': ['B-', 'O-'],
        'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'AB-': ['AB-', 'A-', 'B-', 'O-'],
        'O+': ['O+', 'O-'],
        'O-': ['O-']
    }
    # But here we want to filter Demandes based on Donor's group.
    # So if Donor is 'A+', which Demandes can they respond to?
    # Donor 'A+' can give to 'A+' and 'AB+'.
    donneur_comp_map = {
        'A+': ['A+', 'AB+'],
        'A-': ['A+', 'A-', 'AB+', 'AB-'],
        'B+': ['B+', 'AB+'],
        'B-': ['B+', 'B-', 'AB+', 'AB-'],
        'AB+': ['AB+'],
        'AB-': ['AB+', 'AB-'],
        'O+': ['A+', 'B+', 'AB+', 'O+'],
        'O-': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    }
    return donneur_comp_map.get(groupe, [])

@login_required
def dashboard_donneur(request):
    if hasattr(request.user, 'donneur'):
        donneur = request.user.donneur
        
        # Historique des dons
        dons = Don.objects.filter(donneur=donneur).order_by('-date_don')
        
        # Prochaine date d'éligibilité
        prochaine_date = None
        dernier_don = dons.first()
        if dernier_don:
            jours_attente = 56 if donneur.sexe == 'M' else 84
            prochaine_date = dernier_don.date_don + timedelta(days=jours_attente)
        
        # Demandes urgentes compatibles
        groupes_compatibles = get_compatibilite(donneur.groupe_sanguin)
        demandes_compatibles = DemandeUrgente.objects.filter(
            statut='Ouverte',
            groupe_sanguin__in=groupes_compatibles
        ).order_by('-delai')

        # Mes réponses pour indiquer déjà répondu
        mes_reponses = ReponseAppel.objects.filter(donneur=donneur).values_list('demande_urgente_id', flat=True)
        
        # Mes inscriptions aux campagnes (futures)
        inscriptions = Inscription.objects.filter(
            donneur=donneur, 
            campagne__date__gte=timezone.now().date()
        ).select_related('campagne').order_by('campagne__date', 'creneau_horaire')
        
        return render(request, 'miniProjet/dashboard_donneur.html', {
            'donneur': donneur,
            'dons': dons,
            'prochaine_date': prochaine_date,
            'demandes_compatibles': demandes_compatibles,
            'mes_reponses': mes_reponses,
            'inscriptions': inscriptions,
            'maintenant': timezone.now()
        })
    return redirect('index')

@login_required
def repondre_demande(request, demande_id):
    if hasattr(request.user, 'donneur'):
        demande = get_object_or_404(DemandeUrgente, id=demande_id)
        donneur = request.user.donneur
        
        # Check eligibility (56/84 days rule)
        dons = Don.objects.filter(donneur=donneur).order_by('-date_don')
        dernier_don = dons.first()
        if dernier_don:
            jours_attente = 56 if donneur.sexe == 'M' else 84
            prochaine_date = dernier_don.date_don + timedelta(days=jours_attente)
            if timezone.now() < prochaine_date:
                messages.error(request, "Vous n'êtes pas encore éligible pour donner votre sang (délai de repos non respecté).")
                return redirect('dashboard_donneur')
        
        # Check compatibility just in case
        groupes_compatibles = get_compatibilite(donneur.groupe_sanguin)
        if demande.statut == 'Ouverte' and demande.groupe_sanguin in groupes_compatibles:
            ReponseAppel.objects.get_or_create(
                demande_urgente=demande,
                donneur=donneur,
                defaults={'statut': 'En attente'}
            )
            messages.success(request, 'Votre intention de donner a été enregistrée.')
        else:
            messages.error(request, 'Impossible de répondre à cette demande.')
        return redirect('dashboard_donneur')
    return redirect('index')

@login_required
def enregistrer_don(request):
    if hasattr(request.user, 'donneur'):
        if request.method == 'POST':
            form = DonForm(request.POST)
            if form.is_valid():
                don = form.save(commit=False)
                don.donneur = request.user.donneur
                # Normalement l'hôpital valide, mais on le met non validé par défaut
                don.valide = False
                don.save()
                messages.success(request, 'Votre don a été enregistré avec succès et est en attente de validation par l\'hôpital.')
                return redirect('dashboard_donneur')
        else:
            form = DonForm()
        return render(request, 'miniProjet/don_form.html', {'form': form})
    return redirect('index')

@login_required
def list_campagnes(request):
    if hasattr(request.user, 'donneur'):
        campagnes = Campagne.objects.filter(date__gte=timezone.now().date()).order_by('date')
        return render(request, 'miniProjet/campagnes_list.html', {'campagnes': campagnes})
    return redirect('index')

@login_required
def inscrire_campagne(request, campagne_id):
    if hasattr(request.user, 'donneur'):
        campagne = get_object_or_404(Campagne, id=campagne_id)
        donneur = request.user.donneur
        
        # Check eligibility (56/84 days)
        dons = Don.objects.filter(donneur=donneur).order_by('-date_don')
        dernier_don = dons.first()
        if dernier_don:
            jours_attente = 56 if donneur.sexe == 'M' else 84
            prochaine_date = dernier_don.date_don + timedelta(days=jours_attente)
            if timezone.now() < prochaine_date:
                messages.error(request, "Vous n'êtes pas encore éligible pour donner votre sang (délai de repos non respecté).")
                return redirect('list_campagnes')
        
        # Check if already registered
        if Inscription.objects.filter(campagne=campagne, donneur=donneur).exists():
            messages.warning(request, "Vous êtes déjà inscrit à cette campagne.")
            return redirect('dashboard_donneur')

        if request.method == 'POST':
            form = InscriptionForm(request.POST)
            if form.is_valid():
                creneau = form.cleaned_data['creneau_horaire']
                # Check capacity per slot
                inscrits_slot = Inscription.objects.filter(campagne=campagne, creneau_horaire=creneau).count()
                if inscrits_slot >= campagne.capacite_totale:
                    messages.error(request, "Ce créneau horaire est complet. Veuillez en choisir un autre.")
                else:
                    inscription = form.save(commit=False)
                    inscription.campagne = campagne
                    inscription.donneur = donneur
                    inscription.save()
                    messages.success(request, f"Inscription confirmée pour la campagne à {campagne.lieu} à {creneau.strftime('%H:%M')}.")
                    return redirect('dashboard_donneur')
        else:
            form = InscriptionForm()
        return render(request, 'miniProjet/inscription_campagne_form.html', {'form': form, 'campagne': campagne})
    return redirect('index')

@login_required
def dashboard_admin(request):
    if request.user.is_superuser:
        total_donneurs = Donneur.objects.count()
        total_dons = Don.objects.count()
        
        # Demandes actives par groupe sanguin
        demandes_actives = DemandeUrgente.objects.filter(statut='Ouverte').values('groupe_sanguin').annotate(total=Count('id'))
        
        # Validation des hôpitaux
        hopitaux_attente = Hopital.objects.filter(valide=False)
        
        # Carte simplifiée (Demandes par ville)
        demandes_par_ville = DemandeUrgente.objects.filter(statut='Ouverte').values('hopital__ville').annotate(total=Count('id'))

        return render(request, 'miniProjet/dashboard_admin.html', {
            'total_donneurs': total_donneurs,
            'total_dons': total_dons,
            'demandes_actives': demandes_actives,
            'hopitaux_attente': hopitaux_attente,
            'demandes_par_ville': demandes_par_ville
        })
    return redirect('index')

@login_required
def valider_hopital(request, hopital_id):
    if request.user.is_superuser:
        hopital = get_object_or_404(Hopital, id=hopital_id)
        hopital.valide = True
        hopital.save()
        messages.success(request, f"L'hôpital {hopital.nom} a été validé avec succès.")
        return redirect('dashboard_admin')
    return redirect('index')

@login_required
def export_donneurs_csv(request):
    if request.user.is_superuser:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="donneurs.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Nom Complet', 'Email', 'Groupe Sanguin', 'Sexe', 'Ville', 'Actif'])
        
        donneurs = Donneur.objects.select_related('user').all()
        for d in donneurs:
            writer.writerow([d.user.get_full_name(), d.user.email, d.groupe_sanguin, d.sexe, d.ville, 'Oui' if d.actif else 'Non'])
            
        return response
    return redirect('index')
