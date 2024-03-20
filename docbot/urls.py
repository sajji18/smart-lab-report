from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('eng/',views.eng.as_view(),name="eng"),
    
]