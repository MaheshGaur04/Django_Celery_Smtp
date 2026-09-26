# mailapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, ClockedSchedule
from django.shortcuts import get_object_or_404
import json
from datetime import datetime

from .tasks import send_email_task, send_bulk_email_task

class SendEmailAPIView(APIView):
    def post(self, request):
        recipient = request.data.get('recipient')
        subject = request.data.get('subject')
        message = request.data.get('message')
        html_content = request.data.get('html_content', None)

        if not all([recipient, subject, message]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(recipient, list):
            task = send_bulk_email_task.delay(recipient, subject, message)
        else:
            task = send_email_task.delay(recipient, subject, message, html_content)

        return Response({
            'task_id': task.id,
            'status': 'Email task has been queued for background processing'
        }, status=status.HTTP_202_ACCEPTED)

class EmailStatusAPIView(APIView):
    def get(self, request, task_id):
        task_result = AsyncResult(task_id)
        result = task_result.result
        
        # Convert exceptions to strings so they are JSON serializable
        if isinstance(result, Exception):
            result = str(result)

        return Response({
            'task_id': task_id,
            'status': task_result.status,
            'result': result if task_result.ready() else None
        })

class ScheduleEmailAPIView(APIView):
    def post(self, request):
        recipient = request.data.get('recipient')
        subject = request.data.get('subject')
        message = request.data.get('message')
        schedule_time_str = request.data.get('schedule_time') # Format: YYYY-MM-DD HH:MM:SS

        if not all([recipient, subject, message, schedule_time_str]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Handle Timezone conversion
            naive_time = datetime.strptime(schedule_time_str, '%Y-%m-%d %H:%M:%S')
            aware_time = timezone.make_aware(naive_time)

            # Create a ClockedSchedule for a specific one-time event
            clocked, created = ClockedSchedule.objects.get_or_create(clocked_time=aware_time)

            # Create the dynamic PeriodicTask
            task_name = f"Email to {recipient} at {schedule_time_str}_{timezone.now().timestamp()}"
            
            PeriodicTask.objects.create(
                clocked=clocked,
                name=task_name,
                task='mailapp.tasks.send_email_task',
                args=json.dumps([recipient, subject, message]),
                one_off=True # Deactivates after running once
            )

            return Response({
                'status': 'success',
                'message': f'Email scheduled successfully for {aware_time}'
            }, status=status.HTTP_201_CREATED)
            
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}, status=status.HTTP_400_BAD_REQUEST)

class ScheduledTasksListAPIView(APIView):
    def get(self, request):
        tasks = PeriodicTask.objects.all().values('id', 'name', 'task', 'enabled', 'one_off')
        return Response({'scheduled_tasks': list(tasks)})

class CancelScheduledTaskAPIView(APIView):
    def delete(self, request, task_id):
        task = get_object_or_404(PeriodicTask, id=task_id)
        task.delete()
        return Response({'message': f'Task {task_id} has been cancelled and deleted.'})