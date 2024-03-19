from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Test, Message, TestApplication, BloodTestReport, DiabetesTestReport
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from django.db.models import Q
from django.contrib import messages
from .forms import BloodTestReportForm, DiabetesTestReportForm
from authentication.models import User
# from django.urls import reverse


@login_required
def customer_dashboard(request):
    current_user = request.user
    context = {}
    if current_user.user_type in ["customer", "Customer"]:
        unapplied_tests = Test.objects.exclude(testapplication__user=current_user)
        applied_tests = Test.objects.filter(testapplication__user=current_user)
        context.update({
            'unapplied_tests': unapplied_tests,
            'applied_tests': applied_tests
        })
        return render(request, 'docAI/customer_dashboard.html', context)
    else:
        return JsonResponse({ "message": "Unauthorized" })


@login_required
def doctor_dashboard(request):
    request.session['prev_url'] = request.META.get('HTTP_REFERER', '/')
    current_user = request.user
    if current_user.user_type not in ["doctor", "Doctor"]:
        return JsonResponse({ "message": "Unauthorized" })
    assigned_tests = Test.objects.filter(assigned_to=current_user)
    context = {'assigned_tests': assigned_tests}
    return render(request, 'docAI/doctor_dashboard.html', context)


def check_application(request, test_id):
    current_user = request.user
    test = Test.objects.get(id=test_id)
    has_applied = TestApplication.objects.filter(user=current_user, test=test).exists()
    return render(request, 'check_application.html', {'has_applied': has_applied})


@login_required
def apply_to_test(request, test_id):
    current_user = request.user
    test = Test.objects.get(id=test_id)
    if TestApplication.objects.filter(user=current_user, test=test).exists():
        messages.warning(request, "You have already applied to this test.")
        return redirect('customer_dashboard')
    TestApplication.objects.create(user=current_user, test=test)
    messages.success(request, "You have successfully applied to the test.")
    if test.type == Test.BLOOD_TEST:
        BloodTestReport.objects.create(test=test, applicant=current_user, status='submission')
    elif test.type == Test.DIABETES_TEST:
        DiabetesTestReport.objects.create(test=test, applicant=current_user, status='submission')
    return redirect('customer_dashboard')


@login_required
def doctor_test_detail(request, test_id):
    request.session['prev_url'] = request.META.get('HTTP_REFERER', '/')
    test = get_object_or_404(Test, id=test_id)
    test_applications = TestApplication.objects.filter(test=test)
    context = {
        'test': test,
        'test_applications': test_applications
    }
    return render(request, 'docAI/doctor_test_detail.html', context)


def report_submission(request, report_id):
    report = None
    try:
        report = BloodTestReport.objects.get(id=report_id)
        form_class = BloodTestReportForm
    except BloodTestReport.DoesNotExist:
        pass
    if not report:
        try:
            report = DiabetesTestReport.objects.get(id=report_id)
            form_class = DiabetesTestReportForm
        except DiabetesTestReport.DoesNotExist:
            pass
    if not report:
        return render(request, 'report_not_found.html')
    form = form_class(request.POST or None, instance=report)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if report.status == 'submission':
            report.status = 'evaluation'
        elif report.status == 'evaluation':
            report.status = 'completed'
        report.save()
        if report.status == 'evaluation':
            return redirect('evaluation_section_url')
        elif report.status == 'completed':
            return redirect('completed_section_url')
    return render(request, 'report_submission.html', {'form': form, 'report': report})


@login_required
def doctor_applicant_report(request, test_id, test_type, receiver_id):
    request.session['prev_url'] = request.META.get('HTTP_REFERER', '/')
    report_model = BloodTestReport if test_type == 'blood' else DiabetesTestReport
    report_exists = report_model.objects.filter(test_id=test_id, applicant=receiver_id).exists()
    report = None if not report_exists else report_model.objects.get(test_id=test_id)
    test = get_object_or_404(Test, id=test_id)
    user = request.user
    if user != test.assigned_to and user not in test.testapplication_set.values_list('user', flat=True):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    receiver = get_object_or_404(User, id=receiver_id)
    messages = Message.objects.filter(Q(sender=user, receiver=receiver) | Q(sender=receiver, receiver=user)).order_by('timestamp')
    if request.method == 'POST':
        content = request.POST.get('content')
        sender = user
        try:
            message = Message.objects.create(sender=sender, receiver=receiver, content=content)
            return JsonResponse({'content': message.content})
        except IntegrityError:
            return JsonResponse({'error': 'Failed to create message'}, status=500)
    context = {
        'test': test,
        'user': user,
        'receiver': receiver,
        'messages': messages,
        'report': report
    }
    return render(request, 'docAI/doctor_applicant_report.html', context)


@login_required
def doctor_chat_view(request, customer_id):
    user = request.user
    customer = User.objects.get(id=customer_id)
    messages = Message.objects.filter(Q(sender=user, receiver=customer) | Q(sender=customer, receiver=user)).order_by('timestamp')
    if request.method == 'POST':
        content = request.POST.get('content')
        try:
            message = Message.objects.create(sender=user, receiver=customer, content=content)
            return JsonResponse({'content': message.content})
        except IntegrityError:
            return JsonResponse({'error': 'Failed to create message'}, status=500)
    context = {
        'user': user,
        'customer': customer,
        'messages': messages
    }
    return render(request, 'docAI/doctor_chat_view.html', context)


@login_required
def fetch_messages(request, receiver_id):
    user = request.user
    receiver = get_object_or_404(User, id=receiver_id)
    messages = Message.objects.filter(Q(sender=user, receiver=receiver) | Q(sender=receiver, receiver=user)).order_by('timestamp')
    messages_data = [ {
            'sender': message.sender.username,
            'receiver': message.receiver.username,
            'timestamp': message.timestamp,
            'content': message.content
        } for message in messages]
    return JsonResponse({'messages': messages_data})


@login_required
def send_message(request, receiver_id):
    if request.method == 'POST' and request.is_ajax():
        content = request.POST.get('content')
        receiver = get_object_or_404(User, id=receiver_id)
        sender = request.user
        message = Message.objects.create(sender=sender, receiver=receiver, content=content)
        message_data = {'sender': message.sender.username,
                        'receiver': message.receiver.username,
                        'timestamp': message.timestamp,
                        'content': message.content}
        return JsonResponse({'message': message_data})
    else:
        return JsonResponse({'error': 'Invalid request'})
    
    
@login_required
def doctor_chat_applicants(request):
    unique_applicants = TestApplication.objects.values('user').distinct()
    applicants = []
    for applicant_data in unique_applicants:
        user_id = applicant_data['user']
        user = User.objects.get(id=user_id)
        applicants.append(user)
    return render(request, 'docAI/doctor_chat_applicants.html', {'applicants': applicants})

# @login_required
# def chat_view(request, test_id):
#     test = get_object_or_404(Test, id=test_id)
#     user = request.user
#     if user != test.assigned_to and user not in test.testapplication_set.values_list('user', flat=True):
#         return JsonResponse({'error': 'Unauthorized'}, status=403)
#     messages = Message.objects.filter(test=test).order_by('timestamp')
#     if request.method == 'POST':
#         content = request.POST.get('content')
#         sender = user
#         receiver = test.assigned_to if sender == test.assigned_to else test.testapplication_set.first().user
#         try:
#             message = Message.objects.create(sender=sender, receiver=receiver, test=test, content=content)
#             return JsonResponse({'content': message.content})
#         except IntegrityError:
#             return JsonResponse({'error': 'Failed to create message'}, status=500)
#     context = {
#         'test': test,
#         'user': user,
#         'messages': messages
#     }
#     return render(request, 'docAI/chat.html', context)


# @login_required
# def fetch_messages(request, test_id):
#     user = request.user
#     test = get_object_or_404(Test, id=test_id)
#     if user != test.applied_by and user != test.assigned_to:
#         return JsonResponse({'error': 'Unauthorized'}, status=403)
#     messages = Message.objects.filter(Q(sender=user) | Q(receiver=user), test=test).order_by('timestamp')
#     messages_data = [{'sender': message.sender.username, 'content': message.content} for message in messages]
#     return JsonResponse({'messages': messages_data})


# @login_required
# def send_message(request, test_id):
#     if request.method == 'POST' and request.is_ajax():
#         content = request.POST.get('content')
#         test = get_object_or_404(Test, id=test_id)
#         sender = request.user
#         receiver = test.assigned_to if sender != test.assigned_to else test.applied_by
#         message = Message.objects.create(sender=sender, receiver=receiver, test=test, content=content)
#         return JsonResponse({'content': message.content})
#     else:
#         return JsonResponse({'error': 'Invalid request'})


@login_required
def test_detail(request, test_id):
    test = Test.objects.filter(id=test_id)
    context = {
        test: test
    }
    return render(request, 'docAI/test_detail.html', context)


def back_view(request):
    prev_url = request.session.get('prev_url', '/')
    return redirect(prev_url)


@login_required
def profile(request):
    return render(request, 'docAI/profile.html')


@login_required
def chat(request):
    return render(request, 'docAI/chat.html')