from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Test, Message
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError

@login_required
def dashboard(request):
    current_user = request.user
    context = {}
    
    if current_user.user_type == "customer" or current_user.user_type == "Customer":
        all_tests = Test.objects.all()
        tests = Test.objects.filter(applied_by=current_user.id)
        context.update({
            'all_tests': all_tests,
            'applied_tests': tests
        })
        
    else:
        tests = Test.objects.filter(assigned_to=current_user.id)
        context.update({
            'assigned_tests': tests
        })

    return render(request, 'docAI/dashboard.html', context)


# @login_required
# def chat_view(request, test_id):
#     test = get_object_or_404(Test, id=test_id)
#     messages = Message.objects.filter(test=test)
#     if request.method == 'POST' and 'content' in request.POST:
#         content = request.POST.get('content')
#         sender = request.user
#         receiver = test.assigned_to if request.user == test.applied_by else test.applied_by
#         message = Message.objects.create(sender=sender, receiver=receiver, test=test, content=content)
#         return JsonResponse({'status': 'success'})
#     return render(request, 'docAI/chat.html', {'test': test, 'messages': messages})


# def fetch_messages(request, test_id):
#     messages = Message.objects.filter(test_id=test_id)
#     # print(messages)
#     serialized_messages = [{'sender': message.sender.username, 'content': message.content} for message in messages]
#     print(serialized_messages)
#     return JsonResponse(serialized_messages, safe=False)


def chat_view(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    user = request.user
    messages = Message.objects.filter(test=test)

    if request.method == 'POST':
        content = request.POST.get('content')
        sender = user
        if sender == test.applied_by:
            receiver = test.assigned_to
        elif sender == test.assigned_to:
            receiver = test.applied_by
        else:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        try:
            message = Message.objects.create(sender=sender, receiver=receiver, test=test, content=content)
            return JsonResponse({'content': message.content})
        except IntegrityError:
            return JsonResponse({'error': 'Failed to create message'}, status=500)

    context = {
        'test': test,
        'user': user,
        'messages': messages
    }
    return render(request, 'docAI/chat.html', context)

def send_message(request, test_id):
    if request.method == 'POST' and request.is_ajax():
        content = request.POST.get('content')
        test = get_object_or_404(Test, id=test_id)
        sender = request.user
        receiver = test.assigned_to if sender != test.assigned_to else test.applied_by
        message = Message.objects.create(sender=sender, receiver=receiver, test=test, content=content)
        return JsonResponse({'content': message.content})
    else:
        return JsonResponse({'error': 'Invalid request'})
    
    
def fetch_messages(request, test_id):
    user = request.user
    test = Test.objects.get(id=test_id)
    # Retrieve messages where the current user is either the sender or the receiver and belongs to the specified test
    messages_sent = Message.objects.filter(sender=user, test=test)
    messages_received = Message.objects.filter(receiver=user, test=test)
    # Combine sent and received messages
    messages = list(messages_sent) + list(messages_received)
    # Serialize messages data
    messages_data = [{'sender': message.sender.username, 'content': message.content} for message in messages]
    return JsonResponse({'messages': messages_data})


@login_required
def profile(request):
    return render(request, 'docAI/profile.html')

@login_required
def chat(request):
    return render(request, 'docAI/chat.html')