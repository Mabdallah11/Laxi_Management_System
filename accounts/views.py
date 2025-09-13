from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login, logout
from .forms import TenantCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from django.http import HttpResponse
from django.shortcuts import redirect


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