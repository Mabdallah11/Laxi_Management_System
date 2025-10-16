from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import User  # your custom user
from .models import GeneralMaintenance

class TenantCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']  # add first_name/last_name later if you like

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')

        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Passwords do not match.")

        # Validate password strength against Django's validators
        if p1:
            validate_password(p1, user=None)

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'tenant'
        user.set_password(self.cleaned_data['password1'])  # hash password
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']





class GeneralMaintenanceForm(forms.ModelForm):
    class Meta:
        model = GeneralMaintenance
        fields = ['title', 'description', 'cost', 'status', 'attachment']
