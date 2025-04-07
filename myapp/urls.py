from django.urls import path
from . import views
urlpatterns =[
    path('',views.index, name="main"),
    path('category/<str:category_name>/',views.countryCategory, name="category"),
    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),

    path("checkout1/", views.initiate_payment, name="checkout1"),

    path("verify-payment/<str:reference>/", views.verify_payment, name="verify_payment"),
    path("checkout/", views.checkout, name="checkout"),
    path("order_success/", views.order_success, name="order_success"),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('register-login/', views.register, name='register-login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('get-cart-count/', views.get_cart_count, name='get_cart_count'),
    path('track-parcel/', views.track_parcel, name='track_parcel'),







  ]