from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if not request.POST.get("remember"):
                request.session.set_expiry(0)

            # respect ?next=... if present, else go to dashboard
            nxt = request.GET.get("next") or request.POST.get("next")
            return redirect(nxt or "/accounts/dashboard/")
        messages.error(request, "Invalid username or password")
    return render(request, "accounts/login.html")

@login_required(login_url="/accounts/login/")
def dashboard_view(request):
    return render(request, "accounts/dashboard.html")   # <-- render, no redirect

def logout_view(request):
    logout(request)
    return redirect("/accounts/login/")
from django.shortcuts import redirect

def admin_login_redirect(request):
    nxt = request.GET.get("next", "/dashboard/")
    return redirect(f"/accounts/login/?next={nxt}")
