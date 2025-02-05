from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from .models import Notification
from students.models import Student

def send_notification(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        message = request.POST.get('message')

        if not student_id or not message:
            return JsonResponse({'error': 'Both student_id and message are required'}, status=400)

        try:
            student = Student.objects.get(id=student_id)
            notification = Notification.objects.create(student=student, message=message)
            return JsonResponse({'success': f'Notification successfully sent to {student.name}'}, status=200)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'No student found with the provided ID'}, status=404)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
