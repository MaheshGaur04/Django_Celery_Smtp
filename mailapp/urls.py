from django.urls import path
from .views import (
    SendEmailAPIView, 
    EmailStatusAPIView, 
    ScheduleEmailAPIView, 
    ScheduledTasksListAPIView, 
    CancelScheduledTaskAPIView
)

urlpatterns = [
    path('api/send-email/', SendEmailAPIView.as_view(), name='send-email'),
    path('api/email-status/<str:task_id>/', EmailStatusAPIView.as_view(), name='email-status'),
    
    # New Endpoints
    path('api/schedule-email/', ScheduleEmailAPIView.as_view(), name='schedule-email'),
    path('api/scheduled-tasks/', ScheduledTasksListAPIView.as_view(), name='scheduled-tasks'),
    path('api/cancel-task/<int:task_id>/', CancelScheduledTaskAPIView.as_view(), name='cancel-task'),
]