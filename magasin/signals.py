import requests
from decimal import Decimal
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from .models import Produit, Favori


@receiver(post_save, sender=Produit)
def notify_nouveau_produit(sender, instance, created, **kwargs):
    if not created:
        return

    users = User.objects.filter(is_active=True, is_staff=False).values('email', 'username')
    destinataires = [{'email': u['email'], 'username': u['username']} for u in users if u['email']]

    if not destinataires:
        return
    payload = {
    'produit_nom':   instance.libelle,
    'produit_desc':  instance.description,
    'produit_prix':  str(instance.prix),
    'produit_type':  instance.categorie.name if instance.categorie else '',
    'clients':       destinataires,
}

    try:
        requests.post(settings.N8N_NOUVEAU_PRODUIT_URL, json=payload, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f'[n8n] Erreur nouveau produit : {e}')


# Store old solde value before saving
_produit_old_solde = {}

@receiver(pre_save, sender=Produit)
def store_old_solde(sender, instance, **kwargs):
    """Store the old solde value before the product is saved"""
    try:
        old_instance = Produit.objects.get(pk=instance.pk)
        _produit_old_solde[instance.pk] = old_instance.solde
    except Produit.DoesNotExist:
        _produit_old_solde[instance.pk] = 0


@receiver(post_save, sender=Produit)
def notify_solde_change(sender, instance, created, **kwargs):
    """Notify users with favorited products when a discount is applied"""
    if created:
        return  # Only for updates, not new products
    
    old_solde = _produit_old_solde.get(instance.pk, 0)
    
    # Only send notification if solde was added or increased
    if instance.solde > old_solde and instance.solde > 0:
        # Get users who favorited this product
        favoris = Favori.objects.filter(produit=instance).select_related('user')
        destinataires = [
            {'email': f.user.email, 'username': f.user.username} 
            for f in favoris 
            if f.user.email
        ]
        
        if not destinataires:
            return
        
        # Calculate final price using Decimal
        prix_final = instance.prix * (1 - Decimal(instance.solde) / Decimal(100))
        
        payload = {
            'produit_nom': instance.libelle,
            'produit_prix_ancien': str(instance.prix),
            'produit_prix_new': str(prix_final),
            'solde_pourcentage': instance.solde,
            'clients': destinataires,
        }
        
        try:
            requests.post(settings.N8N_SOLDE_PRODUIT_URL, json=payload, timeout=5)
        except requests.exceptions.RequestException as e:
            print(f'[n8n] Erreur notification solde : {e}')
        finally:
            # Clean up the stored value
            _produit_old_solde.pop(instance.pk, None)
