from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import House, Lease, ServiceChargePayment, MaintenanceRequest  # import your models

admin.site.register(House)
admin.site.register(Lease)
admin.site.register(ServiceChargePayment)
admin.site.register(MaintenanceRequest)
admin.site.register(User, UserAdmin)
