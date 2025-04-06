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
from decimal import Decimal



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

    context = {
        'category': category,
        'posts': posts,
        'cart_count': total_items,
        'error': "Category not found" if not category else None
    }

    return render(request, "category.html", context)

from decimal import Decimal, ROUND_HALF_UP

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



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product  # adjust this if your model is named differently

@csrf_exempt  # Only use temporarily for testing if CSRF is failing
def add_to_cart(request, product_id):
    if request.method == 'POST':
        # Your cart logic here (simplified example)
        product = get_object_or_404(Product, id=product_id)

        # Example: Add product to session-based cart
        cart = request.session.get('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart

        return JsonResponse({'success': True, 'message': 'Item added to cart.'})
    
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



def initiate_payment(request):
    """Renders the payment page"""
    return render(request, "testing-checkout.html", {"paystack_public_key": settings.PAYSTACK_PUBLIC_KEY})

def verify_payment(request, reference):
    """Verifies the transaction with Paystack"""
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    
    response = requests.get(url, headers=headers)
    data = response.json()

    if data["status"] and data["data"]["status"] == "success":
        return JsonResponse({"message": "Payment successful!", "status": "success"})
    
    return JsonResponse({"message": "Payment verification failed!", "status": "failed"})




def checkout(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, "Your cart is empty!")
        return redirect('cart_view')

    # Ensure cart total is a Decimal type
    cart_total = Decimal(str(request.session.get('cart_total', '0')))
    coupon_code = request.session.get('coupon_code', None)
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    
    # Prepare the cart items list with Decimal for price and total calculations
    for product in products:
        quantity = cart.get(str(product.id), 0)
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'price': Decimal(product.price),  # Make sure price is a Decimal
            'total_price': Decimal(product.price) * quantity  # Make sure total is a Decimal
        })

    if request.method == "POST":
        # Save the order details as Decimal for total_price
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            whatsapp_number=request.POST.get('whatsapp_number'),
            country=request.POST.get('country'),
            state=request.POST.get('state'),
            street_address=request.POST.get('street_address'),
            city=request.POST.get('city'),
            zip_code=request.POST.get('zip_code'),
            phone_number=request.POST.get('phone_number'),
            create_account=request.POST.get('create_account') == 'on',
            order_notes=request.POST.get('order_notes'),
            total_price=cart_total,  # Ensure cart total is passed as Decimal
        )

        # Add order items to the database with proper price and quantity
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price'],  # Use Decimal for price
            )

        # Handle coupon usage
        if coupon_code and request.user.is_authenticated:
            coupon = Coupon.objects.filter(code=coupon_code).first()
            if coupon:
                CouponUsage.objects.create(user=request.user, coupon=coupon)

        # Clear cart after placing the order
        request.session['cart'] = {}
        request.session.pop('discount', None)
        request.session.pop('coupon_code', None)
        request.session.pop('cart_total', None)
        request.session.modified = True

        messages.success(request, "Your order has been placed successfully!")
        return redirect("order_success")

    return render(request, "checkout.html", {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_count': sum(cart.values()),
    })




def order_success(request):
    return render(request, "order_success.html")



@login_required
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










