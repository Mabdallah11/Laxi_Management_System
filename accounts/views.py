from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login, logout
from .forms import TenantCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.db import models
from .models import MaintenanceRequest
from django.utils import timezone
from .models import House
from .models import Lease, ServiceChargePayment

User = get_user_model()

@login_required
def maintenance_requests(request):
    # Get all maintenance requests
    requests = MaintenanceRequest.objects.all()
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        requests = requests.filter(status=status_filter)
    
    # Filter by priority if provided
    priority_filter = request.GET.get('priority')
    if priority_filter and priority_filter != 'all':
        requests = requests.filter(priority=priority_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        requests = requests.filter(
            models.Q(issue_description__icontains=search_query) |
            models.Q(tenant__username__icontains=search_query) |
            models.Q(request_id__icontains=search_query)
        )
    
    # Get statistics
    stats = {
        'pending': MaintenanceRequest.objects.filter(status='pending').count(),
        'in_progress': MaintenanceRequest.objects.filter(status='in_progress').count(),
        'completed': MaintenanceRequest.objects.filter(status='completed').count(),
        'high_priority': MaintenanceRequest.objects.filter(priority='high', status__in=['pending', 'in_progress']).count(),
    }
    
    # Get all users for the tenant dropdown (you might want to filter this)
    # For now, getting all users - you can add filtering logic based on your needs
    tenants = User.objects.all()
    
    context = {
        'requests': requests,
        'stats': stats,
        'tenants': tenants,
        'current_status_filter': status_filter,
        'current_priority_filter': priority_filter,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/maintenance_requests.html', context)

@login_required
@require_http_methods(["POST"])
def create_maintenance_request(request):
    try:
        tenant_id = request.POST.get('tenant')
        priority = request.POST.get('priority')
        issue_description = request.POST.get('issue_description')
        additional_notes = request.POST.get('additional_notes', '')
        
        tenant = get_object_or_404(User, id=tenant_id)
        
        # Create the maintenance request
        maintenance_request = MaintenanceRequest.objects.create(
            tenant=tenant,
            unit=getattr(tenant, 'unit', 'N/A'),  # Assuming tenant has a unit field
            issue_description=issue_description,
            priority=priority,
            additional_notes=additional_notes,
        )
        
        messages.success(request, f'Maintenance request {maintenance_request.request_id} created successfully!')
        return redirect('maintenance_requests')
        
    except Exception as e:
        messages.error(request, f'Error creating maintenance request: {str(e)}')
        return redirect('maintenance_requests')

@login_required
def update_request_status(request, request_id):
    if request.method == 'POST':
        maintenance_request = get_object_or_404(MaintenanceRequest, request_id=request_id)
        new_status = request.POST.get('status')
        
        if new_status in ['pending', 'in_progress', 'completed']:
            maintenance_request.status = new_status
            if new_status == 'completed':
                maintenance_request.date_completed = timezone.now()
            maintenance_request.save()
            
            messages.success(request, f'Request {request_id} status updated to {new_status.replace("_", " ").title()}!')
        
        return redirect('maintenance_requests')

@login_required
def delete_maintenance_request(request, request_id):
    if request.method == 'POST':
        maintenance_request = get_object_or_404(MaintenanceRequest, request_id=request_id)
        maintenance_request.delete()
        messages.success(request, f'Maintenance request {request_id} deleted successfully!')
    
    return redirect('maintenance_requests')



def manager_login(request):
    return user_login(request, role="manager")

def tenant_login(request):
    return user_login(request, role="tenant")

def user_logout(request):
    logout(request)
    return redirect('login')  # 👈 back to login page


@login_required
def manager_dashboard(request):
    houses = House.objects.all()
    return render(request, 'accounts/manager_dashboard.html')

@login_required
def tenant_dashboard(request):
    return render(request, 'accounts/tenant_dashboard.html')

@login_required
def maintenance_requests(request):
    # Remove the debug HttpResponse and use render instead
    return render(request, 'accounts/maintenance_requests.html', {})

def home(request):
    return render(request, 'accounts/home.html')

@login_required
def create_tenant(request):
    if request.user.role != 'manager':  # only managers can create tenants
        return redirect('home')

    if request.method == 'POST':
        form = TenantCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manager_dashboard')
    else:
        form = TenantCreationForm()
    return render(request, 'accounts/create_tenant.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role") 

     
      
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.role == "manager":
                return redirect("manager_dashboard")
            elif user.role == "tenant":
                return redirect("tenant_dashboard")
            else:
                return HttpResponse("Unknown role" + str(role))
        else:
            return HttpResponse("Invalid credentials")

    # ✅ GET request → render template with request context
    return render(request, "accounts/login.html")

def house_list(request):
    houses = House.objects.all().order_by('floor', 'number')
    return render(request, 'accounts/house_list.html', {'houses': houses})

@login_required
def tenant_service_charges(request):
    # tenant = logged-in user
    tenant = request.user  

    # get all leases for this tenant (in case of multiple houses)
    leases = tenant.leases.select_related("house").prefetch_related("payments")

    return render(request, "accounts/tenant_service_charges.html", {"leases": leases})

def record_payment(request):
    if request.method == "POST":
        lease_id = request.POST.get("lease")
        amount = request.POST.get("amount")
        payment_date = request.POST.get("payment_date")

        lease = Lease.objects.get(id=lease_id)

        # Use provided date or default to today
        date = payment_date if payment_date else timezone.now().date()

        ServiceChargePayment.objects.create(
            lease=lease,
            amount=amount,
            payment_date=date
        )
        return redirect("record_payment")  # redirect to the same page after saving

    leases = Lease.objects.select_related("tenant", "house").all()
    return render(request, "accounts/record_payment.html", {"leases": leases})

@login_required
def assign_lease(request, house_id):
    house = get_object_or_404(House, id=house_id)

    if request.method == "POST":
        tenant_id = request.POST.get("tenant")
        service_charge = request.POST.get("service_charge")

        tenant = get_object_or_404(User, id=tenant_id, role="tenant")

        # Create lease
        Lease.objects.create(
            tenant=tenant,
            house=house,
            service_charge=service_charge,
        )

        messages.success(request, f"Lease assigned: {house.number} → {tenant.username}")
        return redirect("manager_dashboard")

    tenants = User.objects.filter(role="tenant")
    return render(request, "accounts/assign_lease.html", {"house": house, "tenants": tenants})