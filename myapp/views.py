from django.shortcuts import render,get_object_or_404,redirect
from .models import *
from .models import Product
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Coupon, CouponUsage
from decimal import Decimal
from decimal import Decimal, ROUND_HALF_UP
from .models import CouponUsage
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, Order, OrderItem, Coupon, CouponUsage
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import JsonResponse
import uuid
from django.http import HttpResponse
from decimal import ROUND_DOWN
import json




# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import *

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save user instance
            login(request, user)  # Log the user in immediately
            messages.success(request, "Registration successful.")
            return redirect('main')  # Change 'home' to your desired url name
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('main')  # Change to your desired url name
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'register.html', {'form': form,"messages.error":messages.error})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('main')


# Create your views here.
def index(request):
    cart = request.session.get('cart', {})  # Retrieve cart from session
    total_items = sum(cart.values()) 
    context = {'cart_count': total_items}

    
    return render(request, "index.html", context)


def countryCategory(request, category_name):
    category = RegionCategory.objects.filter(name__iexact=category_name).first()
    
    posts = Product.objects.filter(country_categories=category) if category else []

    cart = request.session.get('cart', {})
    total_items = sum(cart.values())
    request.session['cart'] = cart  # Save the updated cart to the session
    request.session.modified = True  # Mark session as modified

    context = {
        'category': category,
        'posts': posts,
        'cart_count': total_items,
        'error': "Category not found" if not category else None
    }

    return render(request, "category.html", context)



def get_cart_count(request):
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values())
    request.session['cart'] = cart  # Save the updated cart to the session
    request.session.modified = True  # Mark session as modified
    return JsonResponse({'cart_count': cart_count})


def cart_view(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    cart_total = Decimal('0')  # Make sure it's a Decimal from the start

    for product in products:
        quantity = cart[str(product.id)]
        price = Decimal(str(product.price))  # Convert product price to Decimal
        total_price = price * quantity
        cart_total += total_price

        cart_items.append({
            'id': product.id,
            'name': product.name,
            'price': price,
            'quantity': quantity,
            'total': total_price,
            'image': product.imageURL
        })

    # Coupon + discount calculation
    discount = Decimal(str(request.session.get('discount', 0)))  # Always convert session value
    coupon_code = request.session.get('coupon_code', '')
    
    discount_amount = (discount / Decimal('100')) * cart_total
    new_total = cart_total - discount_amount

    # Save total to session
    request.session['cart_total'] = str(new_total)  # Save as str to avoid float issues

    total_items = sum(cart.values())
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_count': total_items,
        'cart_total': cart_total,
        'discount': discount,
        'coupon_code': coupon_code,
        'discount_amount': discount_amount,
        'new_total': new_total
    })



@csrf_exempt  # Only use temporarily for testing if CSRF is failing
def add_to_cart(request, product_id):
    if request.method == 'POST':
        # Your cart logic here (simplified example)
        product = get_object_or_404(Product, id=product_id)

        # Example: Add product to session-based cart
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart

        return JsonResponse({'success': True, 'message': 'Item added to cart.' })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)



# Increase Quantity (AJAX)
def increase_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({'success': True, 'cart_count': sum(cart.values()), 'quantity': cart[product_id]})

# Decrease Quantity (AJAX)
def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] -= 1
        if cart[product_id] <= 0:
            del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({'success': True, 'cart_count': sum(cart.values()), 'quantity': cart.get(product_id, 0)})

# Remove Item (AJAX)
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({'success': True, 'cart_count': sum(cart.values())})

# Clear Cart (AJAX)
def clear_cart(request):
    request.session['cart'] = {}
    request.session.modified = True

    return JsonResponse({'success': True, 'cart_count': 0})




@login_required
def initiate_payment(request, ref):
    # Use ref from URL to get correct order
    order = get_object_or_404(Order, paystack_ref=ref)

    if not order.total_price or order.total_price == 0:
        messages.error(request, "Invalid order amount.")
        return redirect('checkout')

    # Calculate amount in kobo
    amount_in_kobo = (Decimal(order.total_price) * 100).quantize(Decimal('1'), rounding=ROUND_DOWN)

    # Debug logs
    print("=== PAYSTACK DEBUG ===")
    print("Email:", order.email)
    print("Reference:", order.paystack_ref)
    print("Amount in kobo:", amount_in_kobo)
    print("Callback URL:", request.build_absolute_uri("/verify-payment/"))

    paystack_data = {
        "amount": int(amount_in_kobo),
        "email": order.email,
        "reference": order.paystack_ref,
        "callback_url": request.build_absolute_uri("/verify-payment/"),
    }

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    # Make Paystack API request
    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        headers=headers,
        data=json.dumps(paystack_data),
    )

    if response.status_code == 200:
        response_data = response.json()
        return redirect(response_data["data"]["authorization_url"])
    else:
        print("Paystack error:", response.text)
        messages.error(request, "Payment initialization failed. Please try again.")
        return redirect('checkout')






@login_required
def verify_payment(request):
    reference = request.GET.get("reference")

    if not reference:
        return render(request, "payment_error.html", {"error": "No payment reference provided."})

    # Call Paystack verify endpoint
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if data["status"] and data["data"]["status"] == "success":
        # 🎯 THIS is where your code fits
        order = Order.objects.get(paystack_ref=reference)
        order.paid = True
        order.save()

        return render(request, "order_success.html", {"order": order})
    else:
        return render(request, "payment_error.html", {"error": "Payment verification failed."})




from django.views.decorators.http import require_http_methods
import uuid
from decimal import Decimal
@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, "Your cart is empty!")
        return redirect('cart_view')

    if request.method == "GET":
        # ✅ Build the cart_items list for the template
        cart_items = []
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                cart_items.append({'product': product, 'quantity': quantity})
            except Product.DoesNotExist:
                continue  # Skip any products that no longer exist

        # ✅ Render checkout page with cart_items included in context
        return render(request, 'checkout.html', {
            'cart': cart,
            'cart_total': request.session.get('cart_total', 0),
            'cart_items': cart_items,
        })

    # POST request: process form submission
    cart_total = Decimal(str(request.session.get('cart_total', '0')))
    paystack_ref = str(uuid.uuid4())

    # Get form data
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    phone_number = request.POST.get('phone_number')
    country = request.POST.get('country')
    state = request.POST.get('state')
    street_address = request.POST.get('street_address')
    city = request.POST.get('city')
    zip_code = request.POST.get('zip_code')
    order_notes = request.POST.get('order_notes')
    create_account = request.POST.get('create_account') == 'on'

    # Validate
    if not first_name or not last_name or not email or not phone_number or not street_address or not city or not zip_code:
        messages.error(request, "All required fields must be filled out.")
        return redirect('checkout')

    # Save order
    order = Order.objects.create(
        user=request.user,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        country=country,
        state=state,
        street_address=street_address,
        city=city,
        zip_code=zip_code,
        create_account=create_account,
        order_notes=order_notes,
        total_price=cart_total,
        paystack_ref=paystack_ref,
    )

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price,
        )

    coupon_code = request.session.get('coupon_code', '')
    if coupon_code and request.user.is_authenticated:
        coupon = Coupon.objects.filter(code=coupon_code).first()
        if coupon:
            CouponUsage.objects.create(user=request.user, coupon=coupon)

    # Clear cart
    request.session['cart'] = {}
    request.session.pop('discount', None)
    request.session.pop('coupon_code', None)
    request.session.pop('cart_total', None)
    request.session.modified = True

    print("Redirecting with ref:", paystack_ref)
    return redirect('initiate_payment', ref=paystack_ref)





def order_success(request):
    return render(request, "order_success.html")



def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        coupon = Coupon.objects.filter(code__iexact=code, is_active=True).first()
        cart_total = Decimal(str(request.session.get('cart_total', '0')))        

        if not coupon:
            messages.error(request, "Invalid coupon code.")
            return redirect('cart_view')

        if not coupon.is_valid():
            messages.error(request, "This coupon has expired or is no longer active.")
            return redirect('cart_view')

        if cart_total < coupon.min_cart_total:
            messages.error(request, f"Minimum cart total of ${coupon.min_cart_total} required to apply this coupon.")
            return redirect('cart_view')

        # Check if the user has already used this coupon
        if CouponUsage.objects.filter(user=request.user, coupon=coupon).exists():
            messages.error(request, "You have already used this coupon.")
            return redirect('cart_view')

        # Store discount in session
        request.session['coupon_code'] = coupon.code

        request.session['discount'] = float(coupon.discount)

        messages.success(request, f"Coupon applied! You saved {coupon.discount}%")
        return redirect('cart_view')


def track_parcel(request):
    form = TrackParcelForm()
    tracking_info = None
    not_found = False

    if request.method == 'POST':
        form = TrackParcelForm(request.POST)
        if form.is_valid():
            tracking_number = form.cleaned_data['tracking_number']
            try:
                tracking_info = ParcelTracking.objects.select_related('order').get(tracking_number=tracking_number)

            except ParcelTracking.DoesNotExist:
                not_found = True

    return render(request, 'track_parcel.html', {
        'form': form,
        'tracking_info': tracking_info,
        'not_found': not_found,
    })










