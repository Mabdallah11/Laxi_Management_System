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