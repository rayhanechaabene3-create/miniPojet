from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Produit, Category

def inde(request):
    category_id = request.GET.get('category')
    query = request.GET.get('q', '').strip()

    if category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        products = Produit.objects.filter(categorie=selected_category)
        if query:
            products = products.filter(libelle__icontains=query)
            
        return render(request, 'magasin/mesProduit.html', {
            'selected_category': selected_category,
            'products': products,
            'search_query': query,
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

def detail_produit(request, product_id):
    product = Produit.objects.get(id=product_id)
    return render(request, 'magasin/detail.html', {'produit': product})

def add_product(request):
    return render(request, 'magasin/add.html')

def accueil(request):
    return render(request , 'accueil.html' )

def add_to_cart(request, product_id):
    product = Produit.objects.get(id=product_id)
    # Initialize the cart in the session if it doesn't exist
    cart = request.session.get('cart', {})
    
    # Store items by product_id (keys in session dictionary must be strings)
    pid = str(product_id)
    if pid in cart:
        cart[pid]['quantity'] += 1
    else:
        cart[pid] = {
            'quantity': 1,
            'price': float(product.prix),
            'name': product.libelle,
            'image_url': product.image.url if product.image else ''
        }
    
    # Save the updated cart into the session
    request.session['cart'] = cart
    return redirect('panier') # redirect to shopping cart

def add_to_cart_with_quantity(request, product_id):
    if request.method == 'POST':
        product = Produit.objects.get(id=product_id)
        # Initialize the cart in the session if it doesn't exist
        cart = request.session.get('cart', {})
        
        # Get the quantity from the form
        quantity = int(request.POST.get('quantity', 1))
        
        # Store items by product_id (keys in session dictionary must be strings)
        pid = str(product_id)
        if pid in cart:
            cart[pid]['quantity'] += quantity
        else:
            cart[pid] = {
                'quantity': quantity,
                'price': float(product.prix),
                'name': product.libelle,
                'image_url': product.image.url if product.image else ''
            }
        
        # Save the updated cart into the session
        request.session['cart'] = cart
        return redirect('panier')  # redirect to shopping cart
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
        cart = request.session.get('cart', {})
        pid = str(product_id)
        
        if pid in cart:
            new_quantity = int(request.POST.get('quantity', 1))
            if new_quantity > 0:
                cart[pid]['quantity'] = new_quantity
            else:
                del cart[pid]
        
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
    
    if request.method == 'POST':
        # Here you can process the order
        # For now, just clear the cart and redirect
        request.session['cart'] = {}
        return redirect('order_success')
    
    return render(request, 'magasin/checkout.html', {'cart': cart, 'total': round(total, 3)})

def order_success(request):
    return render(request, 'magasin/order_success.html')