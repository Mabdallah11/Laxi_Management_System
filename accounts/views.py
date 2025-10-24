from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login, logout

from laxi_management_system import settings
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
from django.shortcuts import render, get_object_or_404
from .forms import ProfileUpdateForm
from django.db.models import Q
from .models import GeneralMaintenance
from .forms import GeneralMaintenanceForm
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from .models import PaymentTransaction
from django.http import JsonResponse
import json
from django.http import HttpResponse
from django.core.management import call_command
import os

from .utils import (
    generate_payment_reference, 
    verify_paystack_transaction, 
    calculate_outstanding_balance,
    get_paystack_public_key,
    get_paystack_secret_key
)


def load_local_data(request):
    fixture_path = os.path.join(settings.BASE_DIR, 'data.json')  # full path
    call_command('loaddata', fixture_path)
    return HttpResponse("Local database loaded successfully!")

User = get_user_model()


@login_required
def manager_maintenance_requests(request):
    if request.method == "POST":
        req_id = request.POST.get("request_id")
        new_status = request.POST.get("status")
        new_image = request.FILES.get("attachment")  # ✅ Get uploaded image

        try:
            req = MaintenanceRequest.objects.get(id=req_id)

            # Update status
            if new_status:
                req.status = new_status

            # Update attachment if provided
            if new_image:
                req.attachment = new_image

            req.save()
            messages.success(request, f"Updated successfully!")

        except MaintenanceRequest.DoesNotExist:
            messages.error(request, "Request not found.")

    # Fetch all requests
    requests_qs = MaintenanceRequest.objects.all()

    # ✅ Analytics counts
    pending_count = requests_qs.filter(status='pending').count()
    ongoing_count = requests_qs.filter(status='in_progress').count()
    completed_count = requests_qs.filter(status='completed').count()
    older_30_days_count = requests_qs.filter(date_created__lte=timezone.now() - timedelta(days=30)).count()

    context = {
        "requests": requests_qs,
        "status_choices": MaintenanceRequest.STATUS_CHOICES,
        "pending_count": pending_count,
        "ongoing_count": ongoing_count,
        "completed_count": completed_count,
        "older_30_days_count": older_30_days_count,
    }
    return render(request, "accounts/manager_maintenance_requests.html", context)



@login_required
def tenant_create_maintenance_request(request):
    # Get the tenant's active lease
    lease = Lease.objects.filter(tenant=request.user).first()
    requests_qs = MaintenanceRequest.objects.filter(tenant=request.user).order_by('-date_created')

    # Calculate analytics
    pending_count = requests_qs.filter(status="pending").count()
    in_progress_count = requests_qs.filter(status="in_progress").count()
    completed_count = requests_qs.filter(status="completed").count()
    overdue_cutoff = timezone.now() - timedelta(days=30)
    overdue_count = requests_qs.filter(
        status__in=["pending", "in_progress"],
        date_created__lt=overdue_cutoff
    ).count()

    if request.method == "POST":
        issue_description = request.POST.get('issue_description')
        priority = request.POST.get('priority')
        additional_notes = request.POST.get('additional_notes', '')
        attachment = request.FILES.get('attachment')

        unit = lease.house if lease else None

        # Create maintenance request
        new_request = MaintenanceRequest.objects.create(
            tenant=request.user,
            unit=unit,
            issue_description=issue_description,
            priority=priority,
            additional_notes=additional_notes,
            attachment=attachment
        )

        # Send email notification to landlord/manager
        landlord_email = "benson.otieno@strathmore.edu"  # Replace with dynamic email if needed
        send_mail(
            subject=f"New Maintenance Request from {request.user.username}",
            message=f"""
A new maintenance request has been submitted:

Tenant: {request.user.username}
Unit: {unit}
Issue: {issue_description}
Priority: {priority}
Notes: {additional_notes}

Please log in to the system to review the request.
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[landlord_email],
            fail_silently=True
        )

        messages.success(request, "Your maintenance request has been submitted successfully!")
        return redirect('tenant_add_request')  # Refresh the page after submission

    context = {
        "lease": lease,
        "requests": requests_qs,
        "pending_count": pending_count,
        "in_progress_count": in_progress_count,
        "completed_count": completed_count,
        "overdue_count": overdue_count,
    }

    return render(request, "accounts/tenant_add_request.html", context)






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




def user_logout(request):
    logout(request)
    return redirect('login')  # 👈 back to login page


@login_required
def manager_dashboard(request):
    houses = House.objects.all()
    return render(request, 'accounts/manager_dashboard.html')

@login_required
def tenant_dashboard(request):
    # Get tenant's lease and calculate outstanding balance
    lease = Lease.objects.filter(tenant=request.user).first()
    outstanding_balance = calculate_outstanding_balance(lease) if lease else 0
    
    # Get recent payment transactions
    recent_transactions = PaymentTransaction.objects.filter(tenant=request.user).order_by('-created_at')[:3]
    
    context = {
        'lease': lease,
        'outstanding_balance': outstanding_balance,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'accounts/tenant_dashboard.html', context)

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


def manager_login(request):
    return user_login(request, role="manager")

def tenant_login(request):
    return user_login(request, role="tenant")


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
    
    # Get recent Paystack transactions
    recent_paystack_payments = PaymentTransaction.objects.filter(
        status='successful'
    ).select_related('tenant', 'lease__house').order_by('-created_at')[:10]
    
    # Get pending Paystack transactions
    pending_paystack_payments = PaymentTransaction.objects.filter(
        status='pending'
    ).select_related('tenant', 'lease__house').order_by('-created_at')[:5]
    
    context = {
        "leases": leases,
        "recent_paystack_payments": recent_paystack_payments,
        "pending_paystack_payments": pending_paystack_payments,
    }
    return render(request, "accounts/record_payment.html", context)

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

def house_detail(request, house_id):
    house = get_object_or_404(House, id=house_id)
    lease = Lease.objects.filter(house=house).first()
    payments = ServiceChargePayment.objects.filter(lease=lease) if lease else []

    context = {
        "house": house,
        "lease": lease,
        "payments": payments,
    }
    return render(request, "accounts/house_detail.html", context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('tenant_dashboard')  # or use your own dashboard URL
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def manage_tenants(request):
    # Get all tenants
    tenants = User.objects.filter(role="tenant")

    tenant_data = []
    for tenant in tenants:
        lease = Lease.objects.filter(tenant=tenant).select_related("house").first()

        tenant_data.append({
            "username": tenant.username,
            "email": tenant.email,
            "phone": getattr(tenant, "phone", "N/A"),  # safe fallback
            "house": lease.house.number if lease else "Not Assigned",
            "floor": lease.house.floor if lease else "Not Assigned",
            "service_charge": lease.service_charge if lease else "Not Assigned",
        })

    return render(request, "accounts/manage_tenants.html", {"tenant_data": tenant_data})


@login_required
def general_maintenance_manager(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_status':
            rec_id = request.POST.get('rec_id')
            new_status = request.POST.get('status')

            try:
                record = GeneralMaintenance.objects.get(id=rec_id)
                record.status = new_status
                record.save()
                messages.success(request, f"✅ Status updated to {new_status.capitalize()} for '{record.title}'")
            except GeneralMaintenance.DoesNotExist:
                messages.error(request, "❌ Record not found.")

            return redirect('general_maintenance_manager')

        elif action == 'delete':
            rec_id = request.POST.get('rec_id')
            try:
                record = GeneralMaintenance.objects.get(id=rec_id)
                record.delete()
                messages.success(request, f"🗑️ Record '{record.title}' deleted successfully!")
            except GeneralMaintenance.DoesNotExist:
                messages.error(request, "❌ Record not found.")

            return redirect('general_maintenance_manager')

        else:
            form = GeneralMaintenanceForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "✅ New maintenance record added successfully!")
                return redirect('general_maintenance_manager')
            else:
                messages.error(request, "❌ Please correct the errors below.")
    else:
        form = GeneralMaintenanceForm()

    # ✅ Fetch records
    records = GeneralMaintenance.objects.all().order_by('-date')

    # ✅ Analytics
    ongoing_count = records.filter(status='ongoing').count()
    completed_count = records.filter(status='completed').count()
    old_records_count = records.filter(date__lt=now() - timedelta(days=30)).count()

    return render(request, 'accounts/general_maintenance_manager.html', {
        'form': form,
        'records': records,
        'ongoing_count': ongoing_count,
        'completed_count': completed_count,
        'old_records_count': old_records_count,
        'total_count': records.count()
    })



# Tenants can only view
@login_required
def general_maintenance_tenant(request):
    records = GeneralMaintenance.objects.all().order_by('-date')  # Show ALL records
    return render(request, 'accounts/general_maintenance_tenant.html', {'records': records})


# Payment Views
@login_required
def initiate_payment(request, lease_id):
    """Initiate Paystack payment for a lease."""
    if request.user.role != 'tenant':
        return JsonResponse({'error': 'Only tenants can make payments'}, status=403)
    
    try:
        lease = Lease.objects.get(id=lease_id, tenant=request.user)
    except Lease.DoesNotExist:
        return JsonResponse({'error': 'Lease not found'}, status=404)
    
    # Calculate outstanding balance
    outstanding_balance = calculate_outstanding_balance(lease)
    
    if outstanding_balance <= 0:
        return JsonResponse({'error': 'No outstanding balance to pay'}, status=400)
    
    # Generate unique reference
    reference = generate_payment_reference()
    
    # Create payment transaction record
    transaction = PaymentTransaction.objects.create(
        reference=reference,
        lease=lease,
        tenant=request.user,
        amount=outstanding_balance,
        status='pending'
    )
    
    return JsonResponse({
        'public_key': get_paystack_public_key(),
        'reference': reference,
        'amount': float(outstanding_balance) * 100,  # Convert to kobo (Paystack expects amount in kobo)
        'email': request.user.email,
        'callback_url': request.build_absolute_uri('/accounts/payment/callback/')
    })


@login_required
def verify_payment(request, reference):
    """Verify Paystack payment and update records."""
    try:
        transaction = PaymentTransaction.objects.get(reference=reference, tenant=request.user)
    except PaymentTransaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)
    
    # Verify with Paystack API
    secret_key = get_paystack_secret_key()
    if not secret_key:
        return JsonResponse({'error': 'Paystack configuration error'}, status=500)
    
    paystack_response = verify_paystack_transaction(reference, secret_key)
    
    if not paystack_response or paystack_response.get('status') != True:
        transaction.status = 'failed'
        transaction.paystack_response = paystack_response
        transaction.save()
        return JsonResponse({'error': 'Payment verification failed'}, status=400)
    
    # Check if payment was successful
    data = paystack_response.get('data', {})
    if data.get('status') == 'success':
        # Update transaction status
        transaction.status = 'successful'
        transaction.paystack_response = paystack_response
        transaction.save()
        
        # Create ServiceChargePayment record
        ServiceChargePayment.objects.create(
            lease=transaction.lease,
            amount=transaction.amount,
            payment_date=timezone.now()
        )
        
        # Send email notification to manager
        try:
            manager_email = "benson.otieno@strathmore.edu"  # Replace with dynamic email
            send_mail(
                subject=f"Payment Received - {transaction.tenant.username}",
                message=f"""
A payment has been successfully processed:

Tenant: {transaction.tenant.username}
Amount: {transaction.amount}
Transaction Reference: {reference}
Payment Date: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

Please log in to the system to view the payment details.
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[manager_email],
                fail_silently=True
            )
        except Exception as e:
            print(f"Email notification failed: {e}")
        
        return JsonResponse({'success': True, 'message': 'Payment verified successfully'})
    else:
        transaction.status = 'failed'
        transaction.paystack_response = paystack_response
        transaction.save()
        return JsonResponse({'error': 'Payment was not successful'}, status=400)


def payment_callback(request):
    """Handle Paystack redirect after payment."""
    reference = request.GET.get('reference')
    status = request.GET.get('status')
    
    if not reference:
        return render(request, 'accounts/payment_callback.html', {
            'success': False,
            'message': 'No transaction reference provided'
        })
    
    try:
        transaction = PaymentTransaction.objects.get(reference=reference)
        if status == 'success':
            return render(request, 'accounts/payment_callback.html', {
                'success': True,
                'message': 'Payment completed successfully!',
                'reference': reference,
                'amount': transaction.amount
            })
        else:
            return render(request, 'accounts/payment_callback.html', {
                'success': False,
                'message': 'Payment was not successful',
                'reference': reference
            })
    except PaymentTransaction.DoesNotExist:
        return render(request, 'accounts/payment_callback.html', {
            'success': False,
            'message': 'Transaction not found'
        })


@login_required
def payment_history(request):
    """Show tenant's payment transaction history."""
    if request.user.role != 'tenant':
        return redirect('home')
    
    transactions = PaymentTransaction.objects.filter(tenant=request.user).order_by('-created_at')
    
    return render(request, 'accounts/payment_history.html', {
        'transactions': transactions
    })


