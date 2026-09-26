# mailapp/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery.result import AsyncResult
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