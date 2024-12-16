from django.urls import path
from . import views
from . import simpleexample
from docbot.views import customer_chatbot_view

urlpatterns = [
    # Customer
    path('customer-dashboard/', views.customer_dashboard, name="customer_dashboard"),
    path('test/<int:test_id>/', views.test_detail, name="test_detail"),
    path('apply-test/<int:test_id>', views.apply_to_test, name="apply_test"),
    
    # Doctor
    path('doctor-dashboard/', views.doctor_dashboard, name="doctor_dashboard"),
    path('doctor-chat/applicants/', views.doctor_chat_applicants, name='doctor_chat_applicants'),
    path('doctor_test/<int:test_id>', views.doctor_test_detail, name="doctor_test_detail"),
    path('doctor_test/<int:test_id>/type/<str:test_type>/applicant/<int:receiver_id>/', views.doctor_applicant_report, name='doctor_applicant_report'),
    path('doctor_applicant_report_status_update/event/<str:event>/test/<int:test_id>/type/<str:test_type>/applicant/<int:receiver_id>/', views.doctor_applicant_report_status_update, name='doctor_applicant_report_status_update'),
    # path('pdf_file_preview/test/<int:test_id>/type/<str:test_type>/applicant/<int:receiver_id>/', views.pdf_file_preview, name='pdf_file_preview'),
    path('doctor_pdf_preview_page/test/<int:test_id>/type/<str:test_type>/applicant/<int:receiver_id>/', views.doctor_pdf_preview_page, name='doctor_pdf_preview_page'),
    # path('pdf_download/test/<int:test_id>/type/<str:test_type>/applicant/<int:receiver_id>/', views.pdf_download, name='pdf_download'),
    
    # Profile
    path('profile/', views.profile, name="profile"),
    
    # Chat Routes
    path('doctor-chat/applicants/chat/<int:customer_id>', views.doctor_chat_view, name='doctor_chat_view'),
    path('send_message/<int:test_id>/', views.send_message, name='send_message'),
    path('fetch_messages/<int:test_id>/', views.fetch_messages, name='fetch_messages'),
    path('customer_chatbot_view/',customer_chatbot_view.as_view(),name="customer_chatbot_view"),
    
    # Utils
    path('back/', views.back_view, name='back'),
]
