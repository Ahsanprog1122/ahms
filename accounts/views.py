"""accounts views for signup, login, dashboard, and account settings."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import SignUpForm


def signup_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to AHMS, {user.username}! Your account has been created.")
            return redirect("dashboard")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


@login_required
def dashboard_view(request):
    """Placeholder user dashboard."""
    return render(request, "accounts/dashboard.html", {"user": request.user})
