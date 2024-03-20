from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib import messages
from .decorators import unauthenticated_user
from google.oauth2 import id_token
from google.auth.transport import requests
# from backend.settings import GOOGLE_CLIENT_ID

# Create your views here.
@unauthenticated_user
def home(request):
    return render(request, 'authentication/home.html')

@unauthenticated_user
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        user = User.objects.create_user(username=username, password=password, email=email)
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('customer_dashboard')
    else:
        return render(request, 'authentication/signup.html')

@unauthenticated_user
def customer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('customer_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('customer-login')
    else:
        return render(request, 'authentication/customer-login.html')

@unauthenticated_user
def doctor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('doctor_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('doctor-login')
    else:
        return render(request, 'authentication/doctor-login.html')    

# def google_callback(request):
#     tkn = request.POST['id_token']
#     print(tkn)
#     if 'id_token' not in request.POST:
#         return redirect('login')
    
#     token = request.POST['id_token']
#     try:
#         id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
#         email = id_info['email']
#         user = User.objects.filter(email=email).first()
#         if not user:
#             user = User.objects.create_user(email=email)
#         login(request, user)
#         return redirect('dashboard')

#     except Exception as e:
#         print(e)
#         return redirect('login')

@login_required
def logout_view(request):
    logout(request)
    return redirect("/")
