from django import forms
from .models import User

class TenantCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'tenant'
        user.set_password(self.cleaned_data['password'])  # hash password
        if commit:
            user.save()
        return user
