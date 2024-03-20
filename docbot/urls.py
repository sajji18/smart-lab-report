from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('customer_chatbot_view/',views.customer_chatbot_view.as_view(),name="customer_chatbot_view"),
    path('get_messages/', views.get_messages, name='get_messages')
    # path('customer/chatbot_view', views.customer_chatbot_view, name='customer_chatbot_view'),
]

