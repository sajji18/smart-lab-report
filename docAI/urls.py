from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name="dashboard"),
    path('profile/', views.profile, name="profile"),
    path('chat/<int:test_id>/', views.chat_view, name='chat_view'),
    path('send_message/<int:test_id>/', views.send_message, name='send_message'),
    # path('chat/<int:test_id>/', views.chat_view, name='chat_view'),
    path('fetch_messages/<int:test_id>/', views.fetch_messages, name='fetch_messages'),
    path('test/<int:test_id>', views.test_detail, name="test_detail"),
]
