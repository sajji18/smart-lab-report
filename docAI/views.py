import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import pandas as pd
from .models import Test, Message, TestApplication, BloodTestReport, DiabetesTestReport
from django.http import JsonResponse, HttpResponse, QueryDict
from django.db import IntegrityError
from django.db.models import Q
from django.contrib import messages
from .forms import BloodTestReportForm, DiabetesTestReportForm
from authentication.models import User
from . import plotter
from plotly.offline import plot
from django.views.decorators.csrf import csrf_exempt
import plotly.graph_objs as go
import plotly.express as px

# from django.urls import reverse

from django.shortcuts import render
from django_plotly_dash import DjangoDash
from dash import dcc, html, Input, Output, clientside_callback, ClientsideFunction
import dash_mantine_components as dmc
from docAI.data import tradeData

def dash_view():
    # Initialize DjangoDash app
    app = DjangoDash('dash_app', external_scripts=['https://cdn.jsdelivr.net/npm/apexcharts'])

    # Define layout
    app.layout = html.Div(
        children=[
            dcc.Store(id='ApexchartsSampleData', data=tradeData),
            dmc.Center(
                dmc.Paper(
                    shadow="sm",
                    style={'height':'600px', 'width':'800px', 'marginTop':'100px'},
                    children=[
                        html.Div(id='apexAreaChart'),
                        dmc.Center(
                            children=[
                                dmc.SegmentedControl(
                                    id="selectCountryChip",
                                    value="Canada",
                                    data=['Canada', 'USA', 'Australia'],
                                )
                            ]
                        )
                    ]
                )
            )
        ]
    )

#     # Define clientside callback
#     clientside_callback(
#         ClientsideFunction(
#             namespace='apexCharts',
#             function_name='areaChart'
#         ),
#         Output("apexAreaChart", "children"),
#         Input("ApexchartsSampleData", "data"),
#         Input("selectCountryChip", "value"),
#     )
    return app.layout


def scatter(test_id, applicant_id):
        test = Test.objects.get(id=test_id)
        applicant = User.objects.get(id=applicant_id)
        test_model = None
        if test.type == 'blood':
            test_model = BloodTestReport
        else:
            test_model = DiabetesTestReport
        
        test_report = test_model.objects.get(test=test, applicant=applicant)
        # print(test_report.blood_pressure_result)
        x1, y1 = [], []
        if test_model == BloodTestReport:
            x1 = [1,2,3,4,5,6,7,8,9,10,11,12]
            y1 = [test_report.RBC_result,
                test_report.PCV_result,
                test_report.WBC_result,
                test_report.Neutrophils_result,
                test_report.Lymphocytes_result,
                test_report.Eosinophils_result,
                test_report.Monocytes_result,
                test_report.Basophils_result,
                test_report.Platelet_count,
                test_report.hemoglobin_result,
                test_report.blood_pressure_result,
                test_report.cholesterol_level_result
                ]
        else:
            pass

        trace = go.Scatter(
            x = x1,
            y = y1
        )
        layout = dict(
            title='Simple Graph',
            xaxis=dict(range=[min(x1), max(x1)]),
            yaxis = dict(range=[min(y1), max(y1)])
        )

        fig = go.Figure(data=[trace], layout=layout)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div

# def Plotter(request):


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


@csrf_exempt
@login_required
def doctor_applicant_report(request, test_id, test_type, receiver_id):
    # PUT Request
    if request.method == 'PUT':
        raw_data = request.body
        data = QueryDict(raw_data)  # Parse form-urlencoded data
        content = data.get('content')
        test = get_object_or_404(Test, id=test_id)
        applicant = get_object_or_404(User, id=receiver_id)
        report = BloodTestReport.objects.get(test=test, applicant=applicant) if test_type == 'blood' else DiabetesTestReport.objects.get(test=test, applicant=applicant)
        if report:
            if report.status == 'submission':
                report.status = 'evaluation'
            elif report.status == 'evaluation':
                report.status = 'completed'
            report.content = content 
            report.save()
            return JsonResponse({'message': 'Report updated successfully'})
        else:
            return JsonResponse({'error': 'Report not found'}, status=404)
        
    # GET Request
    request.session['prev_url'] = request.META.get('HTTP_REFERER', '/')
    report_model = BloodTestReport if test_type == 'blood' else DiabetesTestReport
    report_exists = report_model.objects.filter(test_id=test_id, applicant=receiver_id).exists()
    report = None if not report_exists else report_model.objects.get(test_id=test_id)
    test = get_object_or_404(Test, id=test_id)
    objs = report_model.objects.all()
    objs_data = []
    if report_model == BloodTestReport:
        objs_data = [
            {
                'RBC_result': x.RBC_result,
                'PCV_result': x.PCV_result,
                'WBC_result': x.WBC_result,
                'Neutrophils_result': x.Neutrophils_result,
                'Lymphocytes_result': x.Lymphocytes_result,
                'Eosinophils_result': x.Eosinophils_result,
                'Monocytes_result': x.Monocytes_result,
                'Basophils_result': x.Basophils_result,
                'Platelet_count': x.Platelet_count,
                'hemoglobin_result': x.hemoglobin_result,
                'blood_pressure_result': x.blood_pressure_result,
                'cholesterol_level_result': x.cholesterol_level_result,
            }  for x in objs
        ]
    else:
        objs_data = [
            {
                'blood_sugar_level_result': x.blood_sugar_level_result,
                'insulin_level_result': x.insulin_level_result,
            }  for x in objs
        ]


    df = pd.DataFrame(objs_data)
    for index, row in df.iterrows():
        fig = px.bar(
            row,  # Using the row as data
            x=row.index,  # Use index as x values
            y=row.values  # Use values as y values
        )
        fig.update_yaxes(autorange="reversed")
        gantt_plot = plot(fig, output_type="div")

    user = request.user
    if user != test.assigned_to and user not in test.testapplication_set.values_list('user', flat=True):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    receiver = get_object_or_404(User, id=receiver_id)
    messages = Message.objects.filter(Q(sender=user, receiver=receiver) | Q(sender=receiver, receiver=user)).order_by('timestamp')
    
    # POST Request
    if request.method == 'POST':
        content = request.POST.get('content')
        test = get_object_or_404(Test, id=test_id)
        applicant = get_object_or_404(User, id=receiver_id)
        report = BloodTestReport.objects.get(test=test, applicant=applicant) if test_type == 'blood' else DiabetesTestReport.objects.get(test=test, applicant=applicant)
        print(content)
        if report:
            if report.status == 'submission':
                report.status = 'evaluation'
            elif report.status == 'evaluation':
                report.status = 'completed'
            report.content = content 
            report.save()
            return redirect('doctor_applicant_report', test_id=test_id, test_type=test_type, receiver_id=receiver_id)
        else:
            return JsonResponse({'error': 'Report not found'}, status=404)
    # plot1 = dash_view()
    context = {
        'test': test,
        'user': user,
        'receiver': receiver,
        'messages': messages,
        'report': report,
        'plot1': scatter(test_id, receiver_id),
        'plot_div': gantt_plot
        # 'plot1': plot1
    }
    return render(request, 'docAI/doctor_applicant_report.html', context)


@csrf_exempt
@login_required
def doctor_applicant_report_status_update(request, test_id, test_type, receiver_id):
    if request.method == 'PUT':
        # Get the test, applicant, and report objects
        test = get_object_or_404(Test, id=test_id)
        applicant = get_object_or_404(User, id=receiver_id)
        report = BloodTestReport.objects.get(test=test, applicant=applicant) if test_type == 'blood' else DiabetesTestReport.objects.get(test=test, applicant=applicant)

        if report:
            if report.status == 'evaluation':
                report.status = 'submission'
            elif report.status == 'completed':
                report.status = 'submission'
            report.save()
            return JsonResponse({'message': 'Report status updated successfully'})
        else:
            return JsonResponse({'error': 'Report not found'}, status=404)



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
def customer_chatbot_view (request):
    return render(request, 'docAI/customer_chatbot.html')
    
    
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
    test = Test.objects.get(id=test_id)
    sender = request.user
    receiver = test.assigned_to
    messages = Message.objects.filter(Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)).order_by('timestamp')
    # Get the report based on test type and applicant ID
    if test.type == Test.BLOOD_TEST:
        report = BloodTestReport.objects.filter(test=test, applicant=request.user).first()
    elif test.type == Test.DIABETES_TEST:
        report = DiabetesTestReport.objects.filter(test=test, applicant=request.user).first()
    else:
        report = None
    
    if request.method == 'POST':
        content = request.POST.get('content')
        try:
            message = Message.objects.create(sender=sender, receiver=receiver, content=content)
            return JsonResponse({'content': message.content})
        except IntegrityError:
            return JsonResponse({'error': 'Failed to create message'}, status=500)
    
    context = {
        'test': test,
        'user': sender,
        'receiver': receiver,
        'messages': messages,
        'report': report 
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