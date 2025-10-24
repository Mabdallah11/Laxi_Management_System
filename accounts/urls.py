from django.urls import path
from . import views
from .views import tenant_create_maintenance_request
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    # --- Home & Auth ---
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('load-data/', views.load_local_data, name='load-data'),
    path('login/', views.login_view, name='login'),
    path('login/manager/', views.manager_login, name='manager_login'),
    path('login/tenant/', views.tenant_login, name='tenant_login'),
    path('logout/', views.user_logout, name='logout'),

    # --- Manager Dashboard ---
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/maintenance/', views.manager_maintenance_requests, name='manager_maintenance_requests'),
    path('manager/create-tenant/', views.create_tenant, name='create_tenant'),
    path('manager/lease/<int:house_id>/', views.assign_lease, name='assign_lease'),
    path('manage-tenants/', views.manage_tenants, name='manage_tenants'),
    path('manager/general-maintenance/', views.general_maintenance_manager, name='general_maintenance_manager'),


    # --- Tenant Dashboard ---
    path('tenant/dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path('tenant/service-charges/', views.tenant_service_charges, name='tenant_service_charges'),
    path('tenant/maintenance/add/', tenant_create_maintenance_request, name='tenant_add_request'),
    path('tenant/general-maintenance/', views.general_maintenance_tenant, name='general_maintenance_tenant'),


    # --- Houses ---
    path('houses/', views.house_list, name='house_list'),
    path('houses/<int:house_id>/', views.house_detail, name='house_detail'),

    # --- Payments ---
    path('record-payment/', views.record_payment, name='record_payment'),

    # --- Profile ---
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    # --- Payments ---
    path('payment/initiate/<int:lease_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/verify/<str:reference>/', views.verify_payment, name='verify_payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('payment/history/', views.payment_history, name='payment_history'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

 
