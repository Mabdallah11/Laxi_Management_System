from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path("login/manager/", views.manager_login, name="manager_login"),
    path("login/tenant/", views.tenant_login, name="tenant_login"),
    path('logout/', views.user_logout, name='logout'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path("manager/maintenance/", views.maintenance_requests, name="maintenance_requests"),
    path('houses/', views.house_list, name='house_list'),
    path("manager/dashboard/maintenance_requests/", views.maintenance_requests, name="maintenance_requests"),
    path('tenant/dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    path("tenant/service-charges/", views.tenant_service_charges, name="tenant_service_charges"),
    path('manager/create-tenant/', views.create_tenant, name='create_tenant'),
    path("record-payment/", views.record_payment, name="record_payment"),
    path("manager/lease/<int:house_id>/", views.assign_lease, name="assign_lease"),

]

