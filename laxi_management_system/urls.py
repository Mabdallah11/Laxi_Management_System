from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),   # 👈 Home will be at http://127.0.0.1:8000/
    path('accounts/', include('accounts.urls')),   # 👈 add this line
]
