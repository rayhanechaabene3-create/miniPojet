from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, View, DetailView, ListView
from django.urls import reverse_lazy
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import timedelta
import csv
import requests
import json
import anthropic
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .forms import (  # pyrefly: ignore [missing-import]
    UserForm, DonneurRegistrationForm, HopitalRegistrationForm,
    DonneurProfileForm, DemandeUrgenteForm, CampagneForm,
    InscriptionForm, DonForm
)
from .models import (  # pyrefly: ignore [missing-import]
    Donneur, Hopital, DemandeUrgente, Don, Campagne,
    ReponseAppel, Inscription, Notification, Analyse
)

class IndexView(TemplateView):
    template_name = 'miniProjet/index.html'

class DonneurInscriptionView(View):
    def get(self, request):
        user_form = UserForm()
        donneur_form = DonneurRegistrationForm()
        return render(request, 'miniProjet/inscription.html', {'user_form': user_form, 'donneur_form': donneur_form})
    
    def post(self, request):
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
        return render(request, 'miniProjet/inscription.html', {'user_form': user_form, 'donneur_form': donneur_form})

class HopitalInscriptionView(View):
    def get(self, request):
        user_form = UserForm()
        hopital_form = HopitalRegistrationForm()
        return render(request, 'miniProjet/hopital_inscription.html', {'user_form': user_form, 'hopital_form': hopital_form})
    
    def post(self, request):
        user_form = UserForm(request.POST)
        hopital_form = HopitalRegistrationForm(request.POST)
        if user_form.is_valid() and hopital_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            hopital = hopital_form.save(commit=False)
            hopital.user = user
            hopital.save()
            messages.success(request, "Inscription hôpital réussie! Votre compte doit être validé par un administrateur.")
            return redirect('connexion')
        return render(request, 'miniProjet/hopital_inscription.html', {'user_form': user_form, 'hopital_form': hopital_form})

class CustomLoginView(LoginView):
    template_name = 'miniProjet/connexion.html'
    
    def form_valid(self, form):
        user = form.get_user()
        if hasattr(user, 'hopital') and not user.hopital.valide:
            messages.error(self.request, "Votre compte hôpital n'est pas encore validé par l'administrateur.")
            from django.contrib.auth import logout
            logout(self.request)
            return self.form_invalid(form)
        return super().form_valid(form)
        
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return reverse_lazy('dashboard_admin')
        if hasattr(user, 'donneur'):
            return reverse_lazy('dashboard_donneur')
        if hasattr(user, 'hopital'):
            return reverse_lazy('dashboard_hopital')
        return reverse_lazy('index')

class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Déconnexion réussie.')
        return redirect('connexion')
    def post(self, request):
        logout(request)
        messages.success(request, 'Déconnexion réussie.')
        return redirect('connexion')

class EditProfileView(LoginRequiredMixin, View):
    def get(self, request):
        if hasattr(request.user, 'donneur'):
            form = DonneurProfileForm(instance=request.user.donneur)
            user_form = UserForm(instance=request.user)
            user_form.fields.pop('password', None)
            return render(request, 'miniProjet/edit_profile_donneur.html', {'form': form, 'user_form': user_form})
        elif hasattr(request.user, 'hopital'):
            user_form = UserForm(instance=request.user)
            user_form.fields.pop('password', None)
            return render(request, 'miniProjet/edit_profile_hopital.html', {'user_form': user_form})
        elif request.user.is_superuser:
            user_form = UserForm(instance=request.user)
            user_form.fields.pop('password', None)
            return render(request, 'miniProjet/edit_profile_admin.html', {'user_form': user_form})
        return redirect('index')

    def post(self, request):
        if hasattr(request.user, 'donneur'):
            form = DonneurProfileForm(request.POST, instance=request.user.donneur)
            user_form = UserForm(request.POST, instance=request.user)
            user_form.fields.pop('password', None)
            if form.is_valid() and user_form.is_valid():
                form.save()
                user_form.save()
                messages.success(request, 'Profil mis à jour avec succès.')
                return redirect('dashboard_donneur')
            return render(request, 'miniProjet/edit_profile_donneur.html', {'form': form, 'user_form': user_form})
        elif hasattr(request.user, 'hopital'):
            user_form = UserForm(request.POST, instance=request.user)
            user_form.fields.pop('password', None)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Profil mis à jour avec succès.')
                return redirect('dashboard_hopital')
            return render(request, 'miniProjet/edit_profile_hopital.html', {'user_form': user_form})
        elif request.user.is_superuser:
            user_form = UserForm(request.POST, instance=request.user)
            user_form.fields.pop('password', None)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Profil administrateur mis à jour avec succès.')
                return redirect('dashboard_admin')
            return render(request, 'miniProjet/edit_profile_admin.html', {'user_form': user_form})
        return redirect('index')

class AccountDeleteView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'miniProjet/delete_account.html')
    def post(self, request):
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Compte supprimé avec succès.')
        return redirect('index')

class ToggleActivationDonneurView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return hasattr(self.request.user, 'donneur')
        
    def get(self, request, *args, **kwargs):
        return redirect('dashboard_donneur')
        
    def post(self, request):
        donneur = request.user.donneur
        donneur.actif = not donneur.actif
        donneur.save()
        messages.success(request, f'Votre compte est maintenant {"actif" if donneur.actif else "inactif"}.')
        return redirect('dashboard_donneur')

# --- HOPITAL VIEWS ---
class HopitalDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'miniProjet/dashboard_hopital.html'
    def test_func(self):
        return hasattr(self.request.user, 'hopital')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['demandes'] = DemandeUrgente.objects.filter(hopital=self.request.user.hopital).order_by('-delai')
        context['campagnes'] = Campagne.objects.filter(hopital=self.request.user.hopital).order_by('-date')
        context['dons_en_attente'] = Don.objects.filter(hopital=self.request.user.hopital, valide=False).order_by('-date_don')
        return context

class CampagneCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Campagne
    form_class = CampagneForm
    template_name = 'miniProjet/campagne_form.html'
    success_url = reverse_lazy('dashboard_hopital')

    def test_func(self):
        user = self.request.user
        return hasattr(user, 'hopital') and user.hopital.valide

    def form_valid(self, form):
        form.instance.hopital = self.request.user.hopital
        messages.success(self.request, 'Campagne de collecte créée avec succès.')
        return super().form_valid(form)

class DemandeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = DemandeUrgente
    form_class = DemandeUrgenteForm
    template_name = 'miniProjet/demande_form.html'
    success_url = reverse_lazy('dashboard_hopital')

    def test_func(self):
        return hasattr(self.request.user, 'hopital')

    def form_valid(self, form):
        form.instance.hopital = self.request.user.hopital
        form.instance.statut = 'Ouverte'
        messages.success(self.request, 'Demande urgente publiée avec succès !')
        return super().form_valid(form)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Créer'
        return context

class DemandeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = DemandeUrgente
    form_class = DemandeUrgenteForm
    template_name = 'miniProjet/demande_form.html'
    pk_url_kwarg = 'demande_id'
    success_url = reverse_lazy('dashboard_hopital')

    def test_func(self):
        demande = self.get_object()
        return hasattr(self.request.user, 'hopital') and demande.hopital == self.request.user.hopital

    def form_valid(self, form):
        messages.success(self.request, 'Demande mise à jour.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Modifier'
        context['demande'] = self.get_object()
        return context

class DemandeCloseView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return hasattr(self.request.user, 'hopital')
    def get(self, request, demande_id):
        demande = get_object_or_404(DemandeUrgente, id=demande_id, hopital=request.user.hopital)
        demande.statut = 'Clôturée'
        demande.save()
        messages.success(request, 'La demande a été clôturée.')
        return redirect('dashboard_hopital')

class ValiderDonView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return hasattr(self.request.user, 'hopital')
        
    def post(self, request, don_id):
        don = get_object_or_404(Don, id=don_id, hopital=request.user.hopital)
        don.valide = True
        don.save()
        messages.success(request, f"Le don de {don.donneur.user.get_full_name() or don.donneur.user.username} a été validé avec succès.")
        return redirect('dashboard_hopital')

class EnvoyerAnalyseView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return hasattr(self.request.user, 'donneur')
        
    def get(self, request, notification_id):
        notif = get_object_or_404(Notification, id=notification_id, destinataire=request.user)
        analyse_existante = Analyse.objects.filter(donneur=request.user.donneur, notification=notif).first()
        return render(request, 'miniProjet/envoyer_analyse.html', {'notification': notif, 'analyse_existante': analyse_existante})

    def post(self, request, notification_id):
        notif = get_object_or_404(Notification, id=notification_id, destinataire=request.user)
        analyse_existante = Analyse.objects.filter(donneur=request.user.donneur, notification=notif).first()
        fichier = request.FILES.get('fichier')
        commentaire = request.POST.get('commentaire', '').strip()
        if fichier and notif.expediteur:
            if analyse_existante:
                analyse_existante.fichier = fichier
                analyse_existante.commentaire = commentaire
                analyse_existante.save()
            else:
                Analyse.objects.create(
                    donneur=request.user.donneur,
                    hopital=notif.expediteur,
                    notification=notif,
                    fichier=fichier,
                    commentaire=commentaire,
                )
            messages.success(request, "Vos analyses ont été envoyées à l'hôpital avec succès.")
            return redirect('dashboard_donneur')
        else:
            messages.error(request, 'Veuillez sélectionner un fichier.')
            return render(request, 'miniProjet/envoyer_analyse.html', {'notification': notif, 'analyse_existante': analyse_existante})

class DemandeReponsesView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = DemandeUrgente
    template_name = 'miniProjet/reponses_demande.html'
    pk_url_kwarg = 'demande_id'
    context_object_name = 'demande'

    def test_func(self):
        return hasattr(self.request.user, 'hopital') and self.get_object().hopital == self.request.user.hopital

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        demande = self.get_object()
        reponses = ReponseAppel.objects.filter(demande_urgente=demande).select_related('donneur__user', 'donneur').order_by('-date_reponse')
        donneur_ids = [r.donneur_id for r in reponses]
        analyses_map = {a.donneur_id: a for a in Analyse.objects.filter(donneur_id__in=donneur_ids)}
        for reponse in reponses:
            reponse.analyse = analyses_map.get(reponse.donneur_id)
        context['reponses'] = reponses
        return context

class DeciderAnalyseView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return hasattr(self.request.user, 'hopital')
        
    def get(self, request, *args, **kwargs):
        return redirect('index')
        
    def post(self, request, analyse_id, decision):
        analyse = get_object_or_404(Analyse, id=analyse_id)
        demande_id = int(request.POST.get('demande_id', 0))
        if decision == 'accepter':
            analyse.statut = 'acceptee'
            msg = f"Bonne nouvelle ! L'hôpital {request.user.hopital.nom} a accepté vos analyses. Vous êtes confirmé comme donneur pour cette demande."
        else:
            analyse.statut = 'refusee'
            msg = f"L'hôpital {request.user.hopital.nom} a refusé vos analyses. Veuillez contacter l'hôpital pour plus d'informations."
        analyse.save()
        Notification.objects.create(
            destinataire=analyse.donneur.user,
            expediteur=request.user.hopital,
            message=msg
        )
        messages.success(request, f"Analyse {'acceptée' if decision == 'accepter' else 'refusée'} avec succès. Le donneur a été notifié.")
        return redirect('view_reponses_demande', demande_id=demande_id)

class EnvoyerNotificationView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return hasattr(self.request.user, 'hopital')
        
    def get(self, request, *args, **kwargs):
        return redirect('index')
        
    def post(self, request, reponse_id):
        reponse = get_object_or_404(ReponseAppel, id=reponse_id, demande_urgente__hopital=request.user.hopital)
        hopital_nom = request.user.hopital.nom
        groupe = reponse.demande_urgente.groupe_sanguin
        Notification.objects.create(
            destinataire=reponse.donneur.user,
            expediteur=request.user.hopital,
            message=f"L'hôpital {hopital_nom} vous demande d'effectuer des analyses médicales pour confirmer votre don de sang ({groupe}). Veuillez vous présenter à l'hôpital muni de votre carte d'identité."
        )
        messages.success(request, f"Notification envoyée à {reponse.donneur.user.get_full_name() or reponse.donneur.user.username}.")
        return redirect('view_reponses_demande', demande_id=reponse.demande_urgente.id)


def get_compatibilite(groupe):
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


def get_context_db(user):
    context = ''
    if not hasattr(user, 'donneur'):
        return 'L\'utilisateur n\'est pas enregistré comme donneur.'

    donneur = user.donneur
    groupe = donneur.groupe_sanguin
    groupes_compatibles = get_compatibilite(groupe)

    demandes = DemandeUrgente.objects.filter(
        statut='Ouverte',
        groupe_sanguin__in=groupes_compatibles,
        delai__gte=timezone.now()
    ).select_related('hopital').order_by('-delai')

    context += '=== INFORMATIONS DONNEUR ===\n'
    context += f'Nom: {user.get_full_name() or user.username}\n'
    context += f'Groupe sanguin: {groupe}\n'
    context += f'Ville: {donneur.ville}\n'
    
    dons = Don.objects.filter(donneur=donneur).order_by('-date_don')
    if dons.exists():
        context += 'Historique des dons :\n'
        for don in dons:
            statut = "Validé" if don.valide else "En attente"
            context += f'- Le {don.date_don.strftime("%d/%m/%Y")} à {don.hopital.nom} ({statut})\n'
        context += '\n'
    else:
        context += 'Historique des dons : Aucun don enregistré\n\n'

    context += f'=== DEMANDES COMPATIBLES AVEC {groupe} ===\n'
    if demandes.exists():
        for d in demandes:
            context += (
                f'- Hôpital: {d.hopital.nom}\n'
                f'  Ville: {d.hopital.ville}\n'
                f'  Adresse: {d.hopital.adresse}\n'
                f'  Groupe demandé: {d.groupe_sanguin}\n'
                f'  Quantité: {d.quantite}\n'
                f'  Délai: {d.delai.strftime("%d/%m/%Y %H:%M")}\n\n'
            )
    else:
        context += 'Aucune demande compatible pour le moment.\n'

    return context


@login_required
@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Requête JSON invalide.'}, status=400)
            
        user_message = data.get("message", "")
        history = data.get("history", [])

        # Récupérer le contexte depuis la DB
        db_context = get_context_db(request.user)

        if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "sk-ant-votre-vraie-cle-api-ici":
            # Mode Simulation
            msg_lower = user_message.lower().strip()
            
            # Analyse de l'historique pour l'état de la conversation
            last_bot_msg = ""
            if history:
                for msg in reversed(history):
                    if msg.get('role') == 'assistant':
                        last_bot_msg = msg.get('content', '').lower()
                        break
            
            if ("âge" in last_bot_msg or "age" in last_bot_msg) and msg_lower.isdigit():
                age = int(msg_lower)
                if age < 18 or age > 70:
                    reply = "❌ Désolé, l'âge limite pour donner du sang est généralement entre 18 et 70 ans."
                else:
                    reply = "Parfait ✅ Quel est votre poids en kg ?"
            elif "poids" in last_bot_msg and msg_lower.isdigit():
                poids = int(msg_lower)
                if poids < 50:
                    reply = "❌ Désolé, vous devez peser au moins 50 kg pour donner du sang. C'est une condition de sécurité pour votre santé."
                else:
                    reply = "✅ C'est parfait ! Vous remplissez les conditions de base de poids et d'âge pour donner votre sang."
            elif 'peux donner' in msg_lower or 'puis-je donner' in msg_lower or 'éligible' in msg_lower or 'condition' in msg_lower:
                reply = "Je vais vérifier ! Quel est votre âge ?"
            elif msg_lower in ['hi', 'hello', 'salut', 'bonjour', 'coucou']:
                reply = "Salut ! Comment puis-je vous aider ?"
            elif 'dernière fois' in msg_lower or 'dernier don' in msg_lower or 'last time' in msg_lower:
                dernier_don = Don.objects.filter(donneur=request.user.donneur).order_by('-date_don').first()
                if dernier_don:
                    reply = f"Votre dernier don a eu lieu le {dernier_don.date_don.strftime('%d/%m/%Y')} à l'hôpital {dernier_don.hopital.nom}."
                else:
                    reply = "Je ne trouve aucun historique de don pour vous dans notre système."
            elif 'historique' in msg_lower or 'mes dons' in msg_lower:
                dons = Don.objects.filter(donneur=request.user.donneur).order_by('-date_don')
                if dons.exists():
                    reply = "Voici l'historique de vos dons :\n"
                    for don in dons:
                        statut = "Validé" if don.valide else "En attente"
                        reply += f"- Le {don.date_don.strftime('%d/%m/%Y')} à {don.hopital.nom} ({statut})\n"
                else:
                    reply = "Je ne trouve aucun historique de don pour vous dans notre système."
            else:
                reply = (
                    "🤖 *Mode Simulation (Clé API non configurée)* 🤖\n\n"
                    f"J'ai bien compris votre demande : \"{user_message}\"\n\n"
                    "Voici les données que j'ai trouvées dans la base pour vous :\n"
                    f"{db_context}\n\n"
                    "*(Pour discuter avec la vraie IA, ajoutez votre clé Anthropic dans settings.py)*"
                )
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": reply})
            return JsonResponse({"reply": reply, "history": history})

        # Construire le system prompt avec les données réelles
        system_prompt = f"""
Tu es un assistant intelligent pour un site de don de sang.
Tu aides les donneurs à trouver les hôpitaux qui ont besoin de leur sang.
Réponds toujours en français, de façon claire et bienveillante.

Voici les données actuelles de la base de données :
{db_context}

Règles :
- Utilise UNIQUEMENT les données ci-dessus pour répondre concernant les hôpitaux
- Si une information n'est pas disponible, dis-le clairement
- Pour les urgences critiques, insiste sur l'importance d'agir vite
- Donne toujours l'adresse et le contact de l'hôpital si disponible
- Si le donneur demande s'il peut donner du sang, demande-lui d'abord son âge. S'il a moins de 18 ans ou plus de 70 ans, c'est refusé. Sinon, demande-lui son poids. S'il pèse moins de 50 kg, explique que c'est refusé par mesure de sécurité pour sa santé. Sinon, confirme qu'il remplit les conditions de base.
"""

        # Appel à l'API Claude via SDK Anthropic
        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            
            # Ensure history only contains 'user' and 'assistant' roles without other keys
            clean_history = []
            for msg in history:
                if msg.get('role') in ['user', 'assistant'] and msg.get('content'):
                    clean_history.append({'role': msg['role'], 'content': msg['content']})
            
            clean_history.append({"role": "user", "content": user_message})

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt,
                messages=clean_history
            )
            
            reply = response.content[0].text
            
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": reply})
            
            return JsonResponse({"reply": reply, "history": history})
        except Exception as e:
            return JsonResponse({'error': f'Erreur API: {str(e)}'}, status=502)

    return render(request, 'miniProjet/chatbot.html', {'is_donneur': hasattr(request.user, 'donneur')})


class DonneurDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'miniProjet/dashboard_donneur.html'

    def test_func(self):
        return hasattr(self.request.user, 'donneur')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        donneur = self.request.user.donneur
        dons = Don.objects.filter(donneur=donneur).order_by('-date_don')
        
        prochaine_date = None
        dernier_don = dons.first()
        if dernier_don:
            jours_attente = 56 if donneur.sexe == 'M' else 84
            prochaine_date = dernier_don.date_don + timedelta(days=jours_attente)
            
        groupes_compatibles = get_compatibilite(donneur.groupe_sanguin)
        demandes_compatibles = DemandeUrgente.objects.filter(
            statut='Ouverte',
            groupe_sanguin__in=groupes_compatibles,
            delai__gte=timezone.now()
        ).order_by('-delai')

        mes_reponses = ReponseAppel.objects.filter(donneur=donneur).values_list('demande_urgente_id', flat=True)
        inscriptions = Inscription.objects.filter(
            donneur=donneur, 
            campagne__date__gte=timezone.now().date()
        ).select_related('campagne').order_by('campagne__date', 'creneau_horaire')
        
        notifications = Notification.objects.filter(destinataire=self.request.user).order_by('-date')
        Notification.objects.filter(destinataire=self.request.user, lu=False).update(lu=True)
        analyses_map = {a.notification_id: a for a in Analyse.objects.filter(donneur=donneur)}
        for notif in notifications:
            notif.analyse = analyses_map.get(notif.id)

        context.update({
            'donneur': donneur,
            'dons': dons,
            'prochaine_date': prochaine_date,
            'demandes_compatibles': demandes_compatibles,
            'mes_reponses': mes_reponses,
            'inscriptions': inscriptions,
            'maintenant': timezone.now(),
            'notifications': notifications,
        })
        return context

class RepondreDemandeView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return hasattr(self.request.user, 'donneur')
        
    def get(self, request, *args, **kwargs):
        return redirect('dashboard_donneur')

    def post(self, request, demande_id):
        demande = get_object_or_404(DemandeUrgente, id=demande_id)
        donneur = request.user.donneur
        dons = Don.objects.filter(donneur=donneur).order_by('-date_don')
        dernier_don = dons.first()
        if dernier_don:
            jours_attente = 56 if donneur.sexe == 'M' else 84
            prochaine_date = dernier_don.date_don + timedelta(days=jours_attente)
            if timezone.now() < prochaine_date:
                messages.error(request, "Vous n'êtes pas encore éligible pour donner votre sang (délai de repos non respecté).")
                return redirect('dashboard_donneur')
        
        groupes_compatibles = get_compatibilite(donneur.groupe_sanguin)
        if demande.statut == 'Ouverte' and demande.groupe_sanguin in groupes_compatibles:
            ReponseAppel.objects.get_or_create(demande_urgente=demande, donneur=donneur, defaults={'statut': 'En attente'})
            messages.success(request, 'Votre intention de donner a été enregistrée.')
        else:
            messages.error(request, 'Impossible de répondre à cette demande.')
        return redirect('dashboard_donneur')

class DonCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Don
    form_class = DonForm
    template_name = 'miniProjet/don_form.html'
    success_url = reverse_lazy('dashboard_donneur')

    def test_func(self):
        return hasattr(self.request.user, 'donneur')

    def form_valid(self, form):
        form.instance.donneur = self.request.user.donneur
        form.instance.valide = False
        messages.success(self.request, "Votre don a été enregistré avec succès et est en attente de validation par l'hôpital.")
        return super().form_valid(form)

class CampagneListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Campagne
    template_name = 'miniProjet/campagnes_list.html'
    context_object_name = 'campagnes'

    def test_func(self):
        return hasattr(self.request.user, 'donneur')

    def handle_no_permission(self):
        return redirect('index')

    def get_queryset(self):
        return Campagne.objects.filter(date__gte=timezone.now().date()).order_by('date')

class InscrireCampagneView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Inscription
    form_class = InscriptionForm
    template_name = 'miniProjet/inscription_campagne_form.html'
    success_url = reverse_lazy('dashboard_donneur')
    
    def test_func(self):
        return hasattr(self.request.user, 'donneur')
        
    def dispatch(self, request, *args, **kwargs):
        self.campagne = get_object_or_404(Campagne, id=self.kwargs['campagne_id'])
        donneur = request.user.donneur
        
        dons = Don.objects.filter(donneur=donneur).order_by('-date_don')
        dernier_don = dons.first()
        if dernier_don:
            jours_attente = 56 if donneur.sexe == 'M' else 84
            prochaine_date = dernier_don.date_don + timedelta(days=jours_attente)
            if timezone.now() < prochaine_date:
                messages.error(request, "Vous n'êtes pas encore éligible pour donner votre sang (délai de repos non respecté).")
                return redirect('list_campagnes')
                
        if Inscription.objects.filter(campagne=self.campagne, donneur=donneur).exists():
            messages.warning(request, "Vous êtes déjà inscrit à cette campagne.")
            return redirect('dashboard_donneur')
            
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campagne'] = self.campagne
        return context

    def form_valid(self, form):
        creneau = form.cleaned_data['creneau_horaire']
        inscrits_slot = Inscription.objects.filter(campagne=self.campagne, creneau_horaire=creneau).count()
        if inscrits_slot >= self.campagne.capacite_totale:
            messages.error(self.request, "Ce créneau horaire est complet. Veuillez en choisir un autre.")
            return self.form_invalid(form)
            
        form.instance.campagne = self.campagne
        form.instance.donneur = self.request.user.donneur
        messages.success(self.request, f"Inscription confirmée pour la campagne à {self.campagne.lieu} à {creneau.strftime('%H:%M')}.")
        return super().form_valid(form)

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'miniProjet/dashboard_admin.html'
    def test_func(self):
        return self.request.user.is_superuser
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_donneurs': Donneur.objects.count(),
            'total_dons': Don.objects.count(),
            'demandes_actives': DemandeUrgente.objects.filter(statut='Ouverte').values('groupe_sanguin').annotate(total=Count('id')),
            'hopitaux_attente': Hopital.objects.filter(valide=False),
            'demandes_par_ville': DemandeUrgente.objects.filter(statut='Ouverte').values('hopital__ville').annotate(total=Count('id')),
            'tous_les_donneurs': Donneur.objects.all().select_related('user'),
            'tous_les_hopitaux': Hopital.objects.all().select_related('user'),
        })
        return context

class ValiderHopitalView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser
        
    def get(self, request, *args, **kwargs):
        return redirect('dashboard_admin')

    def post(self, request, hopital_id):
        hopital = get_object_or_404(Hopital, id=hopital_id)
        hopital.valide = True
        hopital.save()
        messages.success(request, f"L'hôpital {hopital.nom} a été validé avec succès.")
        return redirect('dashboard_admin')

class ExportDonneursCSVView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="donneurs.csv"'
        writer = csv.writer(response)
        writer.writerow(['Nom Complet', 'Email', 'Groupe Sanguin', 'Sexe', 'Ville', 'Actif'])
        donneurs = Donneur.objects.select_related('user').all()
        for d in donneurs:
            writer.writerow([d.user.get_full_name(), d.user.email, d.groupe_sanguin, d.sexe, d.ville, 'Oui' if d.actif else 'Non'])
        return response
