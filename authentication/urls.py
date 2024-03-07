from django.urls import path
from authentication import views as AUTH_VIEWS

urlpatterns = [
    path('', AUTH_VIEWS.home, name="home")
]
