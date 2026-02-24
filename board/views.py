from django.contrib.auth import logout as _logout
from django.shortcuts import render, redirect
from django.urls import reverse


def index(request):
    return render(request, "board/index.html", {})


def logout(request):
    if request.user.is_authenticated:
        _logout(request)
    return redirect(reverse('index'))
