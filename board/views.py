from django.contrib.auth import logout as _logout, authenticate, login as _login
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms


def index(request):
    if not request.user.is_authenticated:
        return redirect(reverse("board:login"))
    return render(request, "board/index.html", {})


def logout(request):
    if request.user.is_authenticated:
        _logout(request)
    return redirect(reverse("board:index"))

# login form that uses email and password for authentication.
class LoginForm(forms.Form):
    username = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput)


def login(request):
    if request.user.is_authenticated:
        return redirect(reverse("board:index"))

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                _login(request, user)
                redirect_url = reverse("board:index")
                if getattr(request, "htmx", False):
                    response = redirect(redirect_url)
                    response["HX-Redirect"] = redirect_url
                    return response
                return redirect(redirect_url)
            else:
                form.add_error(None, "Invalid email or password.")
    else:
        form = LoginForm()

    template_name = "board/partials/login_form.html" if getattr(request, "htmx", False) else "board/login.html"
    return render(request, template_name, {"form": form})
