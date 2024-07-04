from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.user_type == 'customer' or request.user.user_type == 'Customer':
                return redirect('customer_dashboard')
            else:
                return redirect('doctor_dashboard')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func
