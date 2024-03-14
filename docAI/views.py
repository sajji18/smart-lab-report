from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Test

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