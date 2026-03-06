from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]
        widgets = {"email": forms.EmailInput(attrs={"required": True})}

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if not email:
            raise forms.ValidationError("Email is required.")
        elif User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use.")

        return email
