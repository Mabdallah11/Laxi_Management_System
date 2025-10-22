from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import House, Lease, ServiceChargePayment, MaintenanceRequest  # import your models

admin.site.register(House)
admin.site.register(Lease)
admin.site.register(ServiceChargePayment)
admin.site.register(MaintenanceRequest)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Display role in the list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')

    # Make role editable in the detail view
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

    # Also show it when creating a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    