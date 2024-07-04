from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login-customer/", views.customer_login, name="customer-login"),
    path("login-doctor/", views.doctor_login, name="doctor-login"),
    # path('google/login/', views.google_login, name='google_login'),
    # path('google/callback/', views.google_callback, name='google_callback'),
    path("logout/", views.logout_view, name="logout")
]
