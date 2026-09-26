from django.urls import path
from .views import SendEmailAPIView, EmailStatusAPIView

urlpatterns = [
    path('api/send-email/', SendEmailAPIView.as_view(), name='send-email'),
    path('api/email-status/<str:task_id>/', EmailStatusAPIView.as_view(), name='email-status'),
]