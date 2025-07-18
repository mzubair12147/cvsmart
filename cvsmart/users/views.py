from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.models import User


# Create your views here.
def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            error = "Both fields are required."
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                print("i am authenticated bruh!")
                login(request, user)
                return redirect("/")  # Replace 'home' with your target URL name
            else:
                error = "Invalid username or password."

    return render(
        request,
        "users/login.html",
        context={"project_name": getattr(settings, "PROJECT_NAME"), "error": error},
    )


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username") or None
        password1 = request.POST.get("password1") or None
        password2 = request.POST.get("password2") or None
        error = None
        if not username or not password1 or not password2:
            error = "All Fields are required"
        if password1 != password2:
            error = "Both Passwords should be equal"
        if User.objects.filter(username=username).exists():
            error = "User already exists"

        if error:
            return render(
                request,
                "users/signup.html",
                context={
                    "project_name": getattr(settings, "PROJECT_NAME"),
                    "error": error,
                },
                status=400,
            )

        new_user = User.objects.create_user(username=username, password=password1)
        new_user.save()
        login(request, new_user)
        return redirect("/")

    return render(
        request,
        "users/signup.html",
        context={"project_name": getattr(settings, "PROJECT_NAME")},
        status=200,
    )

def logout_view(request):
    logout(request)
    return redirect("/")