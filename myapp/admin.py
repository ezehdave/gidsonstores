from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(RegionCategory)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Coupon)
admin.site.register(CouponUsage)
admin.site.register(ParcelTracking)




