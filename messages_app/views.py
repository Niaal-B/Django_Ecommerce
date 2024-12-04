from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Message
from django.contrib.auth.models import User

# Send Message
@login_required
def send_message(request):
    if request.method == "POST":
        content = request.POST.get('content')
        admin = User.objects.filter(is_superuser=True).first()  # Fetch admin user
        Message.objects.create(sender=request.user, receiver=admin, content=content)
        return redirect('message_list')
    return render(request, 'messages_app/send_message.html')

# List Messages
@login_required
def message_list(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'messages_app/message_list.html', {'messages': messages})

# Reply to a Message (Admin)
@login_required
def reply_message(request, message_id):
    message = Message.objects.get(id=message_id)
    if request.method == "POST":
        content = request.POST.get('content')
        Message.objects.create(sender=request.user, receiver=message.sender, content=content)
        return redirect('message_list')
    return render(request, 'messages_app/reply_message.html', {'message': message})
