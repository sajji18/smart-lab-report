from django.urls import path
from . import views

urlpatterns = [
    # Customer
    path('customer-dashboard/', views.customer_dashboard, name="customer_dashboard"),
    path('test/<int:test_id>/', views.test_detail, name="test_detail"),
    path('apply-test/<int:test_id>', views.apply_to_test, name="apply_test"),
    
    # Doctor
    path('doctor-dashboard/', views.doctor_dashboard, name="doctor_dashboard"),
    path('doctor_test/<int:test_id>', views.doctor_test_detail, name="doctor_test_detail"),
    path('doctor_test/<int:test_id>/type/<str:test_type>/applicant/<int:receiver_id>', views.doctor_applicant_report, name='doctor_applicant_report'),
    
    # Profile
    path('profile/', views.profile, name="profile"),
    
    # Chat Routes
    path('send_message/<int:test_id>/', views.send_message, name='send_message'),
    path('fetch_messages/<int:test_id>/', views.fetch_messages, name='fetch_messages'),
]
