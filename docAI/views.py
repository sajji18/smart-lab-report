import json
import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
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
import subprocess
from django.shortcuts import render
from django_plotly_dash import DjangoDash
from dash import dcc, html, Input, Output, clientside_callback, ClientsideFunction
import dash_mantine_components as dmc
from docAI.data import tradeData
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa

'''
    Function: dash_view
    Parameters: None
    Return Type: html.Div
    Description:
        - Initialize a django dash app using apexcharts cdn
        - Define the layout, styling and children
        - Return the layout
'''
def dash_view():
    app = DjangoDash('dash_app', external_scripts=['https://cdn.jsdelivr.net/npm/apexcharts'])
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
    return app.layout


'''
    Function: scatter
    Parameters: {test_id: Test Id, applicant_id: User Id}
    Return Type: string
    Description: 
        - Fetch the test and applicant based on the ids
        - Fetch the test report type based on the test type
        - Once Report Model is Found, Test report data can be acquired
        - Create a scatter plot using plotly and acquired data
        - Return the plotly div
'''
def scatter(test_id, applicant_id):
        test = Test.objects.get(id=test_id)
        applicant = User.objects.get(id=applicant_id)
        test_model = None
        if test.type == 'blood':
            test_model = BloodTestReport
        else:
            test_model = DiabetesTestReport
        test_report = test_model.objects.get(test=test, applicant=applicant)
        x1, y1 = [], []
        if test_model == BloodTestReport:
            x1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            y1 = [
                test_report.RBC_result,
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
            x1 = [1, 2]
            y1 = [
                test_report.insulin_level_result,
                test_report.blood_sugar_level_result
            ]
        trace = go.Scatter(
            x = x1,
            y = y1
        )
        layout = dict(
            title = 'Simple Graph',
            xaxis = dict(range=[min(x1), max(x1)]),
            yaxis = dict(range=[min(y1), max(y1)])
        )
        fig = go.Figure(data=[trace], layout=layout)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div


'''
    Function: customer_dashboard
    Parameters: request
    Return Type: render 
    Description: 
        - Fetch the current user making request
        - Check if the user is a customer, If not then cannot access the customer dashboard
        - If the user is a customer, fetch all {applied and unapplied} tests to be shown on dashboard and store in context
        - Return the customer dashboard with the created context
'''
@login_required
def customer_dashboard(request):
    current_user = request.user
    context = {}
    if current_user.user_type in ["customer", "Customer"]:
        unapplied_tests = Test.objects.exclude(testapplication__user=current_user)
        applied_tests = Test.objects.filter(testapplication__user=current_user)
        context.update(
            {
            'unapplied_tests': unapplied_tests,
            'applied_tests': applied_tests
            }
        )
        return render(request, 'docAI/customer_dashboard.html', context)
    else:
        return JsonResponse({ "message": "Unauthorized" })


'''
    Function: doctor_dashboard
    Parameters: request
    Return Type: render
    Description:
        - Set request.session['prev_url'] to the previous url, to keep track of the page we come from
        - Fetch the current user making request
        - Check if the user is a doctor, If not, then they cannot access the doctor dashboard
        - If the user is a doctor, fetch all tests assigned to the doctor and store in context
        - Return the doctor dashboard with the created context
'''
@login_required
def doctor_dashboard(request):
    request.session['prev_url'] = request.META.get('HTTP_REFERER', '/')
    current_user = request.user
    if current_user.user_type not in ["doctor", "Doctor"]:
        return JsonResponse({ "message": "Unauthorized" })
    assigned_tests = Test.objects.filter(assigned_to=current_user)
    context = {'assigned_tests': assigned_tests}
    return render(request, 'docAI/doctor_dashboard.html', context)


'''
    Currently It is not integrated in Frontend and Test Application is done from the Admin Superuser Account
'''
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


'''
    Function: doctor_test_detail
    Parameters: request, test_id: Test Id
    Return Type: render
    Description:
        - Set request.session['prev_url'] to the previous url, to keep track of the page we come from
        - Fetch the test based on the test_id
        - Fetch all test applications for the given test and store in context
        - Return the doctor test detail page with the created context
'''
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


'''
    Function: doctor_applicant_report
    Parameters: request, test_id: Test Id, test_type: Test Type, receiver_id: User Id
    Return Type: render
    Description:
        - If the request method is POST:
            - Fetch the test based on the test_id
            - Fetch the applicant based on the receiver_id
            - Fetch the report based on the test type
            -Update the test report based on the data received from the frontend
        - If the request method is GET:
            - Fetch the test based on the test_id
            - Fetch the applicant based on the receiver_id
            - Fetch the report based on the test type
            - Based on report and report Model, Create a dataframe and plot the graph with plotly and create context
            - Return the doctor applicant report page with the created context
'''
@csrf_exempt
@login_required
def doctor_applicant_report(request, test_id, test_type, receiver_id):
    if request.method == 'POST':
        print(request.POST)
        test = get_object_or_404(Test, id=test_id)
        applicant = get_object_or_404(User, id=receiver_id)
        report = BloodTestReport.objects.get(test=test, applicant=applicant) if test_type == 'blood' else DiabetesTestReport.objects.get(test=test, applicant=applicant)
        print(report)
        if report:
            if report.status == 'submission':
                report.status = 'evaluation'
                if test_type == 'blood':
                    report.RBC_result = request.POST.get('RBC_result') 
                    report.PCV_result = request.POST.get('PCV_result') 
                    report.WBC_result = request.POST.get('WBC_result') 
                    report.Neutrophils_result = request.POST.get('Neutrophils_result') 
                    report.Lymphocytes_result = request.POST.get('Lymphocytes_result') 
                    report.Eosinophils_result = request.POST.get('Eosinophils_result') 
                    report.Monocytes_result = request.POST.get('Monocytes_result') 
                    report.Basophils_result = request.POST.get('Basophils_result') 
                    report.Platelet_count = request.POST.get('Platelet_count') 
                    report.hemoglobin_result = request.POST.get('hemoglobin_result') 
                    report.blood_pressure_result = request.POST.get('blood_pressure_result') 
                    report.cholesterol_level_result = request.POST.get('cholesterol_level_result') 
                else:
                    report.blood_sugar_level_result = request.POST.get('blood_sugar_level_result') 
                    report.insulin_level_result = request.POST.get('insulin_level_result') 
            elif report.status == 'evaluation':
                report.status = 'completed'
                if test_type == 'blood':
                    report.include_RBC_Result = request.POST.get('include_RBC_Result') == 'True'
                    report.include_PCV_Result = request.POST.get('include_PCV_Result') == 'True'
                    report.include_WBC_Result = request.POST.get('include_WBC_Result') == 'True'
                    report.include_Neutrophils_Result = request.POST.get('include_Neutrophils_Result') == 'True'
                    report.include_Lymphocytes_Result = request.POST.get('include_Lymphocytes_Result') == 'True'
                    report.include_Eosinophils_Result = request.POST.get('include_Eosinophils_Result') == 'True'
                    report.include_Monocytes_Result = request.POST.get('include_Monocytes_Result') == 'True'
                    report.include_Basophils_Result = request.POST.get('include_Basophils_Result') == 'True'
                    report.include_Platelet_Count = request.POST.get('include_Platelet_Count') == 'True'
                    report.include_hemoglobin_Result = request.POST.get('include_hemoglobin_Result') == 'True'
                    report.include_blood_pressure_Result = request.POST.get('include_blood_pressure_Result') == 'True'
                    report.include_cholesterol_level_Result = request.POST.get('include_cholesterol_level_Result') == 'True'
                else:
                    print('type of data from frontend is: ')
                    print(type(request.POST.get('include_blood_sugar_level_Result')))
                    report.include_blood_sugar_level_Result = request.POST.get('include_blood_sugar_level_Result') == 'True'
                    report.include_insulin_level_Result = request.POST.get('include_insulin_level_Result') == 'True'
            report.save()
            return JsonResponse({'message': 'Report updated successfully'})
        else:
            return JsonResponse({'error': 'Report not found'}, status=404)

    elif request.method == 'GET':
        print(test_id, test_type, receiver_id)
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
                x = row.index,  # Use index as x values
                y = row.values  # Use values as y values
            )
        fig.update_yaxes(autorange="reversed")
        gantt_plot = plot(fig, output_type="div")
        user = request.user
        if user != test.assigned_to and user not in test.testapplication_set.values_list('user', flat=True):
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        receiver = get_object_or_404(User, id=receiver_id)
        messages = Message.objects.filter(Q(sender=user, receiver=receiver) | Q(sender=receiver, receiver=user)).order_by('timestamp')
        context = {
            'test': test,
            'user': user,
            'receiver': receiver,
            'messages': messages,
            'report': report,
            'plot_div': gantt_plot,
            # 'plot1': scatter(test_id, receiver_id)
        }
        return render(request, 'docAI/doctor_applicant_report.html', context)
    return JsonResponse({'error': 'Invalid request'})


'''
    Function: doctor_applicant_report_status_update
    Parameters: request, event: "next" | "back", test_id: Test Id, test_type: Test Type, receiver_id: User Id
    Return Type: JsonResponse
    Description:
        - If the request method is PUT:
            - Fetch the test based on the test_id
            - Fetch the applicant based on the receiver_id
            - Fetch the report based on the test type
            - Update the report status based on the event received from the frontend, event is "next" | "back"
            - Return a JsonResponse with the message "Report status updated successfully"
'''
@csrf_exempt
@login_required
def doctor_applicant_report_status_update(request, event, test_id, test_type, receiver_id):
    print('this is update method on next or back button')
    print(request.method)
    if request.method == 'PUT':
        test = get_object_or_404(Test, id=test_id)
        applicant = get_object_or_404(User, id=receiver_id)
        report = BloodTestReport.objects.get(test=test, applicant=applicant) if test_type == 'blood' else DiabetesTestReport.objects.get(test=test, applicant=applicant)
        if report:
            if event == 'back':
                if report.status == 'evaluation':
                    report.status = 'submission'
                elif report.status == 'completed':
                    report.status = 'submission'
            elif event == 'next':
                if report.status == 'submission':
                    report.status = 'evaluation'
                elif report.status == 'evaluation':
                    report.status = 'completed'
            report.save()
            return JsonResponse({'message': 'Report status updated successfully'})
        else:
            return JsonResponse({'error': 'Report not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'})


'''
    Function: doctor_pdf_preview_page
    Parameters: request, test_id: Test Id, test_type: Test Type, receiver_id: User Id
    Return Type: render | JsonResponse
    Description:
        - Based on the user type, the handler creates context for the report preview page
'''
def doctor_pdf_preview_page (request, test_id, test_type, receiver_id):
    if request.method == 'GET':
        if request.user.user_type not in ['customer', 'Customer']:
            test = get_object_or_404(Test, id=test_id)
            receiver = get_object_or_404(User, id=receiver_id)
            doctor = request.user
            report_model = BloodTestReport if test_type == 'blood' else DiabetesTestReport
            report_exists = report_model.objects.filter(test_id=test_id, applicant=receiver_id).exists()
            report = None if not report_exists else report_model.objects.get(test_id=test_id)
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
                    x = row.index,  # Use index as x values
                    y = row.values  # Use values as y values
                )
            fig.update_yaxes(autorange="reversed")
            gantt_plot = plot(fig, output_type="div")
            context = {
                'doctor': doctor,
                'test': test,
                'receiver': receiver,
                'report': report,
                'plot_div': gantt_plot
            }
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'redirect_url': reverse('doctor_pdf_preview_page', args=[test_id, test_type, receiver_id])})
            return render(request, 'docAI/doctor_pdf_preview_page.html', context)
        else:
            test = get_object_or_404(Test, id=test_id)
            report_model = BloodTestReport if test_type == 'blood' else DiabetesTestReport
            report_exists = report_model.objects.filter(test_id=test_id, applicant=request.user).exists()
            report = None if not report_exists else report_model.objects.get(test_id=test_id)
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
                    x = row.index,  # Use index as x values
                    y = row.values  # Use values as y values
                )
            fig.update_yaxes(autorange="reversed")
            gantt_plot = plot(fig, output_type="div")
            context = {
                'test': test,
                'report': report,
                'plot_div': gantt_plot
            }
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'redirect_url': reverse('doctor_pdf_preview_page', args=[test_id, test_type, receiver_id])})
            return render(request, 'docAI/doctor_pdf_preview_page.html', context)
    return JsonResponse({'error': 'Invalid request'})


'''
    Currently Not using the below handler
    It's supposed to generate a pdf of the pdf_preview page and send to the user on clicking of preview option
'''
# def pdf_download (request, test_id, test_type, receiver_id):
#     test = get_object_or_404(Test, id=test_id)
#     receiver = get_object_or_404(User, id=receiver_id)
#     doctor = request.user
#     report_model = BloodTestReport if test_type == 'blood' else DiabetesTestReport
#     report_exists = report_model.objects.filter(test_id=test_id, applicant=receiver_id).exists()
#     report = None if not report_exists else report_model.objects.get(test_id=test_id)
#     objs = report_model.objects.all()
#     objs_data = []
#     if report_model == BloodTestReport:
#         objs_data = [
#             {
#                 'RBC_result': x.RBC_result,
#                 'PCV_result': x.PCV_result,
#                 'WBC_result': x.WBC_result,
#                 'Neutrophils_result': x.Neutrophils_result,
#                 'Lymphocytes_result': x.Lymphocytes_result,
#                 'Eosinophils_result': x.Eosinophils_result,
#                 'Monocytes_result': x.Monocytes_result,
#                 'Basophils_result': x.Basophils_result,
#                 'Platelet_count': x.Platelet_count,
#                 'hemoglobin_result': x.hemoglobin_result,
#                 'blood_pressure_result': x.blood_pressure_result,
#                 'cholesterol_level_result': x.cholesterol_level_result,
#             }  for x in objs
#         ]
#     else:
#         objs_data = [
#             {
#                 'blood_sugar_level_result': x.blood_sugar_level_result,
#                 'insulin_level_result': x.insulin_level_result,
#             }  for x in objs
#         ]
#     df = pd.DataFrame(objs_data)
#     for index, row in df.iterrows():
#         fig = px.bar(
#             row,  # Using the row as data
#             x = row.index,  # Use index as x values
#             y = row.values  # Use values as y values
#         )
#     fig.update_yaxes(autorange="reversed")
#     # gantt_plot = plot(fig, output_type="div")
#     print('Image generation is about to start')
#     img_path = os.path.join(settings.MEDIA_ROOT, 'gantt_plot.jpeg')
#     print(img_path)
#     fig.write_image(img_path)
#     img_url = os.path.join(settings.MEDIA_URL, 'gantt_plot.jpeg')
#     print(img_url)
#     context = {
#         'doctor': doctor,
#         'test': test,
#         'receiver': receiver,
#         'report': report,
#         'plot_img_url': img_url
#     }
#     # Using xhtml2pdf
#     template = get_template('docAI/doctor_pdf_preview_page.html')
#     html = template.render(context)
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
#     if not pisa.err:
#         return HttpResponse(result.getvalue(), content_type='application/pdf')
#     return None


'''
    Function: pdf_file_preview
    Parameters: {request, test_id, test_type, receiver_id}
    Return Type: JsonResponse
    Description:
        - run the puppeteer script for pdf generation using python subprocess
'''
# def pdf_file_preview(request, test_id, test_type, receiver_id):
#     url = f'http://localhost:8000'
#     # Running the puppeteer script for my pdf generation
#     subprocess.run(['node', 'puppeteer/index.js', url, str(test_id), str(test_type), str(receiver_id)])
#     # Finally, Sending PDF to User
#     return JsonResponse({'message': 'PDF Generated Successfully'})


'''
    Function: doctor_chat_view
    Parameters: {request, customer_id}
    Return Type: render
    Description:
        - Fetch the current user making request
        - Fetch the customer based on the customer_id
        - Fetch all messages between the user and customer and store in context
        - If the request method is POST:
            - Fetch the content from the request and create a new message
            - Return a JsonResponse with the message content
        - Else:
            - Return the doctor chat view with the created context
'''
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


'''
    Function: fetch_messages
    Parameters: {request, receiver_id}
    Return Type: JsonResponse
    Description:
        - Fetch the current user making request
        - Fetch the receiver based on the receiver_id
        - Fetch all messages between the user and receiver and store in messages_data
        - Return a JsonResponse with the messages_data
'''
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


'''
    Function: send_message
    Parameters: {request, receiver_id}
    Return Type: JsonResponse
    Description:
        - Fetch the content from the request
        - Fetch the receiver based on the receiver_id
        - Fetch the sender based on the request user
        - Create a new message and store in message_data
        - Return a JsonResponse with the message_data
'''
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


'''
    Function: test_detail
    Parameters: {request, test_id}
    Return Type: render
    Description:
        - Fetch the test based on the test_id
        - Fetch the sender based on the request user
        - Fetch the receiver based on the test assigned_to
        - Fetch all messages between the sender and receiver and store in messages
        - If the request method is POST:
            - Fetch the content from the request
            - Create a new message and store in message
            - Return a JsonResponse with the message content
        - Else:
            - If the test type is Blood Test:
                - Fetch the Blood Test Report based on the test and applicant
            - If the test type is Diabetes Test:
                - Fetch the Diabetes Test Report based on the test and applicant
            - Else:
                - Set report to None
            - Create a context with the test, sender, receiver, messages and report
            - Return the test detail page with the created context
'''
@login_required
def test_detail(request, test_id):
    test = Test.objects.get(id=test_id)
    sender = request.user
    receiver = test.assigned_to
    messages = Message.objects.filter(Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)).order_by('timestamp')
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