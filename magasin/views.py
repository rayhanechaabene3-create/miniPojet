from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, UpdateView, DeleteView, ListView, DetailView
)
from .models import Produit, Category, Commande, CommandeItem, Favori
from .forms import ProductForm, CategoryForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .serializers import CategorySerializer, ProduitSerializer

def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url='connexion_magasin')(view_func)

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to check if user is authenticated and staff member"""
    login_url = 'connexion_magasin'
    
    def test_func(self):
        return self.request.user.is_staff

class AdminDashboardView(StaffRequiredMixin, ListView):
    """Admin dashboard showing products and orders"""
    model = Produit
    template_name = 'magasin/admin_dashboard.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        return Produit.objects.select_related('categorie', 'Fournisseur').all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['commandes'] = Commande.objects.prefetch_related('items').order_by('-dateCde')
        context['categories'] = Category.objects.all()
        return context

admin_dashboard = AdminDashboardView.as_view()


# Category Generic Views
class CategoryCreateView(StaffRequiredMixin, CreateView):
    """Create a new category"""
    model = Category
    form_class = CategoryForm
    template_name = 'magasin/admin_category_form.html'
    success_url = reverse_lazy('admin_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Ajouter'
        return context

admin_add_category = CategoryCreateView.as_view()


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    """Update an existing category"""
    model = Category
    form_class = CategoryForm
    template_name = 'magasin/admin_category_form.html'
    success_url = reverse_lazy('admin_dashboard')
    pk_url_kwarg = 'category_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Modifier'
        return context

admin_edit_category = CategoryUpdateView.as_view()


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    """Delete a category"""
    model = Category
    template_name = 'magasin/admin_confirm_delete_category.html'
    success_url = reverse_lazy('admin_dashboard')
    pk_url_kwarg = 'category_id'

admin_delete_category = CategoryDeleteView.as_view()


# Product Generic Views
class ProductCreateView(StaffRequiredMixin, CreateView):
    """Create a new product"""
    model = Produit
    form_class = ProductForm
    template_name = 'magasin/admin_product_form.html'
    success_url = reverse_lazy('admin_dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Ajouter'
        return context

admin_add_product = ProductCreateView.as_view()


class ProductUpdateView(StaffRequiredMixin, UpdateView):
    """Update an existing product"""
    model = Produit
    form_class = ProductForm
    template_name = 'magasin/admin_product_form.html'
    success_url = reverse_lazy('admin_dashboard')
    pk_url_kwarg = 'product_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Modifier'
        return context
    
    def form_valid(self, form):
        old_product = Produit.objects.get(pk=self.get_object().pk)
        old_solde = old_product.solde
        self.object = form.save()
        
        # Notify if discount was added or increased
        if self.object.solde > old_solde and self.object.solde > 0:
            favoris_count = Favori.objects.filter(produit=self.object).count()
            if favoris_count > 0:
                messages.success(self.request, 
                    f'✉️ Produit mis à jour et {favoris_count} utilisateur(s) ont été notifiés du solde!')
            else:
                messages.info(self.request, 
                    'Produit mis à jour. Aucun utilisateur favori pour envoyer les notifications.')
        else:
            messages.success(self.request, 'Produit mis à jour avec succès.')
        
        return super(UpdateView, self).form_valid(form)

admin_edit_product = ProductUpdateView.as_view()


class ProductDeleteView(StaffRequiredMixin, DeleteView):
    """Delete a product"""
    model = Produit
    template_name = 'magasin/admin_confirm_delete.html'
    success_url = reverse_lazy('admin_dashboard')
    pk_url_kwarg = 'product_id'

admin_delete_product = ProductDeleteView.as_view()


@login_required(login_url='connexion_magasin')
def toggle_favori(request, product_id):
    try:
        produit = Produit.objects.get(id=product_id)
    except Produit.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Produit introuvable'}, status=404)
        messages.error(request, "❌ Le produit n'existe pas.")
        return redirect('inde')
    
    favori, created = Favori.objects.get_or_create(user=request.user, produit=produit)
    
    if not created:
        favori.delete()
        is_favorite = False
        message = f"♡ {produit.libelle} retiré des favoris"
    else:
        is_favorite = True
        message = f"♥ {produit.libelle} ajouté aux favoris"
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'is_favorite': is_favorite})
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'inde'))

class FavoritesListView(LoginRequiredMixin, ListView):
    """Display user's favorite products"""
    model = Favori
    template_name = 'magasin/favoris.html'
    context_object_name = 'favoris'
    login_url = 'connexion_magasin'
    paginate_by = 12
    
    def get_queryset(self):
        return Favori.objects.filter(
            user=self.request.user
        ).select_related('produit').order_by('-id')

mes_favoris = FavoritesListView.as_view()

@login_required(login_url='connexion_magasin')
def profil(request):
    user = request.user
    message = None
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        if new_password:
            user.set_password(new_password)
            user.save()
            login(request, user)
        else:
            user.save()
        message = 'Profil mis à jour avec succès.'
    return render(request, 'magasin/profil.html', {'message': message})

def inscription_magasin(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_staff else 'inde')
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.email = request.POST.get('email', '').strip()
        user.save()
        return redirect('connexion_magasin')
    return render(request, 'magasin/inscription.html', {'form': form})

def connexion_magasin(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_staff else 'inde')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('admin_dashboard' if user.is_staff else 'inde')
    return render(request, 'magasin/connexion.html', {'form': form})

def set_language_magasin(request):
    lang = request.POST.get('language', 'fr')
    if lang in ('fr', 'en'):
        request.session['lang_magasin'] = lang
    return redirect(request.META.get('HTTP_REFERER', 'inde'))

def deconnexion_magasin(request):
    logout(request)
    return redirect('connexion_magasin')

@login_required(login_url='connexion_magasin')
def inde(request):
    category_id = request.GET.get('category')
    query = request.GET.get('q', '').strip()
    favori_ids = set(Favori.objects.filter(user=request.user).values_list('produit_id', flat=True))

    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        products = Produit.objects.filter(categorie=selected_category)
        if query:
            products = products.filter(libelle__icontains=query)
        return render(request, 'magasin/mesProduit.html', {
            'selected_category': selected_category,
            'products': products,
            'search_query': query,
            'favori_ids': favori_ids,
        })

    categories = Category.objects.prefetch_related('produit_set').all()
    category_groups = []
    for category in categories:
        products_qs = Produit.objects.filter(categorie=category)
        if query:
            products_qs = products_qs.filter(libelle__icontains=query)
        products = list(products_qs)
        if products:
            category_groups.append({'category': category, 'products': products})

    return render(request, 'magasin/mesProduit.html', {
        'categories': categories,
        'category_groups': category_groups,
        'search_query': query,
        'favori_ids': favori_ids,
    })

def category_products(request, category_id):
    selected_category = get_object_or_404(Category, id=category_id)
    products = Produit.objects.filter(categorie=selected_category)
    return render(request, 'magasin/mesProduit.html', {
        'selected_category': selected_category,
        'products': products,
    })

def base(request):
    return render(request,'magasin/base.html')

def navbar(request):
    products = Produit.objects.all()
    categories= Category.objects.all()
    return render(request,'magasin/navbar.html', {'products': products, 'categories': categories})

class ProductDetailView(DetailView):
    """Display detailed view of a product"""
    model = Produit
    template_name = 'magasin/detail.html'
    context_object_name = 'produit'
    pk_url_kwarg = 'product_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favori.objects.filter(
                user=self.request.user, 
                produit=self.object
            ).exists()
        return context

detail_produit = ProductDetailView.as_view()

def add_product(request):
    return render(request, 'magasin/add.html')

def accueil(request):
    return render(request , 'accueil.html' )

def add_to_cart(request, product_id):
    try:
        product = Produit.objects.get(id=product_id)
    except Produit.DoesNotExist:
        messages.error(request, "❌ Le produit n'existe pas.")
        return redirect('inde')
    
    cart = request.session.get('cart', {})
    pid = str(product_id)
    
    # Check if product is out of stock
    if product.quantite <= 0:
        messages.error(request, f"❌ Le produit '{product.libelle}' est actuellement indisponible.")
        return redirect('inde')
    
    # Check total quantity in cart
    current_quantity = cart.get(pid, {}).get('quantity', 0)
    if current_quantity + 1 > product.quantite:
        messages.warning(request, f"⚠️ Seulement {product.quantite} {product.libelle}(s) disponible(s). Vous en avez déjà {current_quantity} dans le panier.")
        return redirect('inde')
    
    if pid in cart:
        cart[pid]['quantity'] += 1
    else:
        cart[pid] = {
            'quantity': 1,
            'price': float(product.prix),
            'name': product.libelle,
            'image_url': product.image.url if product.image else ''
        }
    
    request.session['cart'] = cart
    messages.success(request, f"✅ {product.libelle} ajouté au panier.")
    return redirect('panier')

def add_to_cart_with_quantity(request, product_id):
    if request.method == 'POST':
        try:
            product = Produit.objects.get(id=product_id)
        except Produit.DoesNotExist:
            messages.error(request, "❌ Le produit n'existe pas.")
            return redirect('inde')
        
        cart = request.session.get('cart', {})
        
        # Get the quantity from the form
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity <= 0:
                messages.error(request, "❌ La quantité doit être supérieure à 0.")
                return redirect('detail_produit', product_id=product_id)
        except ValueError:
            messages.error(request, "❌ Quantité invalide.")
            return redirect('detail_produit', product_id=product_id)
        
        # Check if product is out of stock
        if product.quantite <= 0:
            messages.error(request, f"❌ Le produit '{product.libelle}' est actuellement indisponible.")
            return redirect('detail_produit', product_id=product_id)
        
        pid = str(product_id)
        current_quantity = cart.get(pid, {}).get('quantity', 0)
        
        # Check total quantity against available stock
        if current_quantity + quantity > product.quantite:
            messages.warning(request, f"⚠️ Seulement {product.quantite} {product.libelle}(s) disponible(s). Vous en avez déjà {current_quantity} dans le panier. Maximum à ajouter: {product.quantite - current_quantity}.")
            return redirect('detail_produit', product_id=product_id)
        
        if pid in cart:
            cart[pid]['quantity'] += quantity
        else:
            cart[pid] = {
                'quantity': quantity,
                'price': float(product.prix),
                'name': product.libelle,
                'image_url': product.image.url if product.image else ''
            }
        
        request.session['cart'] = cart
        messages.success(request, f"✅ {quantity} {product.libelle}(s) ajouté(s) au panier.")
        return redirect('panier')
    return redirect('inde')

def panier(request):
    cart = request.session.get('cart', {})
    total = 0
    # Create a copy so we can add template-specific variables without saving them to session yet
    for key, item in cart.items():
        item['row_total'] = round(item['price'] * item['quantity'], 3)
        total += item['row_total']
        
    return render(request, 'magasin/panier.html', {'cart': cart, 'total': round(total, 3)})

def update_cart(request, product_id):
    if request.method == 'POST':
        try:
            product = Produit.objects.get(id=product_id)
        except Produit.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Produit introuvable'})
            messages.error(request, "❌ Le produit n'existe pas.")
            return redirect('panier')
        
        cart = request.session.get('cart', {})
        pid = str(product_id)
        
        if pid in cart:
            try:
                new_quantity = int(request.POST.get('quantity', 1))
            except ValueError:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Quantité invalide'})
                messages.error(request, "❌ Quantité invalide.")
                return redirect('panier')
            
            if new_quantity > 0:
                # Check if new quantity exceeds available stock
                if new_quantity > product.quantite:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': f'Seulement {product.quantite} disponible(s)'})
                    messages.error(request, f"❌ Seulement {product.quantite} {product.libelle}(s) disponible(s).")
                    return redirect('panier')
                cart[pid]['quantity'] = new_quantity
                if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    messages.success(request, f"✅ Quantité mise à jour.")
            else:
                del cart[pid]
                if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    messages.info(request, f"ℹ️ {product.libelle} retiré du panier.")
        
        request.session['cart'] = cart
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('panier')

def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        pid = str(product_id)
        
        if pid in cart:
            del cart[pid]
        
        request.session['cart'] = cart
        return redirect('panier')

def checkout(request):
    cart = request.session.get('cart', {})
    total = 0
    for key, item in cart.items():
        item['row_total'] = round(item['price'] * item['quantity'], 3)
        total += item['row_total']

    if request.method == 'POST' and cart:
        # Validate all items in cart still have available quantity
        out_of_stock_items = []
        for key, item in cart.items():
            try:
                product = Produit.objects.get(id=int(key))
                if item['quantity'] > product.quantite:
                    out_of_stock_items.append({
                        'name': item['name'],
                        'requested': item['quantity'],
                        'available': product.quantite
                    })
            except (Produit.DoesNotExist, ValueError):
                out_of_stock_items.append({
                    'name': item['name'],
                    'error': 'Produit supprimé'
                })
        
        if out_of_stock_items:
            error_msg = "❌ Certains articles ne sont plus disponibles en quantité suffisante:\n"
            for item in out_of_stock_items:
                if 'error' in item:
                    error_msg += f"- {item['name']}: {item['error']}\n"
                else:
                    error_msg += f"- {item['name']}: {item['available']}/{item['requested']} disponible(s)\n"
            messages.error(request, error_msg)
            return redirect('panier')
        
        try:
            commande = Commande.objects.create(
                client=request.user.username,
                nom=request.POST.get('nom', '').strip(),
                email=request.POST.get('email', '').strip(),
                telephone=request.POST.get('telephone', '').strip(),
                adresse=request.POST.get('adresse', '').strip(),
                totalCde=round(total, 3),
            )
            
            for key, item in cart.items():
                CommandeItem.objects.create(
                    commande=commande,
                    produit_nom=item['name'],
                    quantite=item['quantity'],
                    prix_unitaire=item['price'],
                )
            
            request.session['cart'] = {}

            # Send to n8n after items are saved
            try:
                import requests as req
                from django.conf import settings
                items_payload = []
                for item in commande.items.all():
                    items_payload.append({
                        'produit_nom': item.produit_nom,
                        'quantite': item.quantite,
                        'prix_unitaire': str(item.prix_unitaire),
                        'total': str(item.total()),
                    })
                req.post(settings.N8N_WEBHOOK_URL, json={
                    'order_id':  commande.id,
                    'nom':       commande.nom,
                    'email':     commande.email,
                    'telephone': commande.telephone,
                    'adresse':   commande.adresse,
                    'date':      str(commande.dateCde),
                    'total':     str(commande.totalCde),
                    'items':     items_payload,
                }, timeout=5)
            except Exception as e:
                print(f'[n8n] Erreur : {e}')

            return redirect('order_success')
        
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la création de la commande: {str(e)}")
            return redirect('panier')

    return render(request, 'magasin/checkout.html', {'cart': cart, 'total': round(total, 3)})

def order_success(request):
    return render(request, 'magasin/order_success.html')

# API ViewSets with Enhanced Features
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API views"""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewset(viewsets.ModelViewSet):
    """API ViewSet for Categories with filtering"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'id']
    ordering = ['name']
    permission_classes = [IsAuthenticated]


class ProduitViewset(viewsets.ModelViewSet):
    """API ViewSet for Products with advanced filtering, pagination and search"""
    serializer_class = ProduitSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categorie', 'type', 'Fournisseur']
    search_fields = ['libelle', 'description']
    ordering_fields = ['prix', 'quantite', 'solde', 'id']
    ordering = ['-id']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Enhanced queryset with:
        - Filtering by category_id (backward compatible)
        - Select related for performance
        - Price filtering
        """
        queryset = Produit.objects.select_related('categorie', 'Fournisseur').all()
        
        # Backward compatibility with old categorie_id parameter
        categorie_id = self.request.GET.get('categorie_id')
        if categorie_id is not None:
            queryset = queryset.filter(categorie_id=categorie_id)
        
        # Price range filtering
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        if min_price is not None:
            try:
                queryset = queryset.filter(prix__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price is not None:
            try:
                queryset = queryset.filter(prix__lte=float(max_price))
            except ValueError:
                pass
        
        # Filter in-stock products
        in_stock = self.request.GET.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(quantite__gt=0)
        
        return queryset

# ── React API endpoints ──────────────────────────────────────────
from rest_framework.decorators import api_view, permission_classes
from .serializers import CommandeSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def api_csrf(request):
    from django.middleware.csrf import get_token
    return Response({'csrfToken': get_token(request)})

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    user = authenticate(request, username=request.data.get('username'), password=request.data.get('password'))
    if user:
        login(request, user)
        return Response({'id': user.id, 'username': user.username, 'email': user.email, 'is_staff': user.is_staff})
    return Response({'error': 'Identifiants incorrects'}, status=400)

@api_view(['POST'])
def api_logout(request):
    logout(request)
    return Response({'ok': True})

@api_view(['GET'])
@permission_classes([AllowAny])
def api_me(request):
    if request.user.is_authenticated:
        u = request.user
        return Response({'id': u.id, 'username': u.username, 'email': u.email, 'first_name': u.first_name, 'last_name': u.last_name, 'is_staff': u.is_staff})
    return Response({'error': 'Non authentifie'}, status=401)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_inscription(request):
    from django.contrib.auth.models import User
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password1', '').strip()
    if not username or not password:
        return Response({'error': 'Champs obligatoires manquants'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'error': "Nom d'utilisateur deja pris"}, status=400)
    User.objects.create_user(username=username, email=email, password=password)
    return Response({'ok': True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_profil(request):
    u = request.user
    u.first_name = request.data.get('first_name', u.first_name)
    u.last_name = request.data.get('last_name', u.last_name)
    u.email = request.data.get('email', u.email)
    new_password = request.data.get('new_password', '').strip()
    if new_password:
        u.set_password(new_password)
        u.save()
        login(request, u)
    else:
        u.save()
    return Response({'ok': True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_commande(request):
    items_data = request.data.get('items', [])
    total = request.data.get('totalCde', 0)
    commande = Commande.objects.create(
        client=request.user.username,
        nom=request.data.get('nom', ''),
        email=request.data.get('email', ''),
        telephone=request.data.get('telephone', ''),
        adresse=request.data.get('adresse', ''),
        totalCde=total,
    )
    for item in items_data:
        CommandeItem.objects.create(
            commande=commande,
            produit_nom=item['produit_nom'],
            quantite=item['quantite'],
            prix_unitaire=item['prix_unitaire'],
        )
    try:
        import requests as req
        from django.conf import settings
        items_payload = [{'produit_nom': i.produit_nom, 'quantite': i.quantite, 'prix_unitaire': str(i.prix_unitaire), 'total': str(i.total())} for i in commande.items.all()]
        req.post(settings.N8N_WEBHOOK_URL, json={'order_id': commande.id, 'nom': commande.nom, 'email': commande.email, 'telephone': commande.telephone, 'adresse': commande.adresse, 'date': str(commande.dateCde), 'total': str(commande.totalCde), 'items': items_payload}, timeout=5)
    except Exception:
        pass
    return Response({'ok': True, 'commande_id': commande.id})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_favoris(request):
    favoris = Favori.objects.filter(user=request.user).select_related('produit')
    data = [{'id': f.id, 'produit': ProduitSerializer(f.produit, context={'request': request}).data} for f in favoris]
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_commandes_list(request):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=403)
    commandes = Commande.objects.prefetch_related('items').order_by('-dateCde')
    return Response(CommandeSerializer(commandes, many=True).data)
