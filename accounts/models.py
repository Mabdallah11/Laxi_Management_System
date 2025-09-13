from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

class MaintenanceRequest(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    request_id = models.CharField(max_length=20, unique=True, blank=True)
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='maintenance_requests')
    unit = models.CharField(max_length=50)
    issue_description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    additional_notes = models.TextField(blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_completed = models.DateTimeField(null=True, blank=True)
    assigned_to = models.CharField(max_length=100, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.request_id:
            # Auto-generate request ID
            last_request = MaintenanceRequest.objects.all().order_by('id').last()
            if last_request:
                last_id = int(last_request.request_id[3:])
                self.request_id = f'MR{last_id + 1:03d}'
            else:
                self.request_id = 'MR001'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.request_id} - {self.tenant.username} - {self.issue_description[:50]}"
    
    class Meta:
        ordering = ['-date_created']

class User(AbstractUser):
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('tenant', 'Tenant'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')

    def __str__(self):
        return f"{self.username} ({self.role})"
