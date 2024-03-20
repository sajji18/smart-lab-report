from django.shortcuts import render, redirect, reverse
from authentication.models import User
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from docbot.chat import get_response, bot_name
from datetime import date, timedelta
import speech_recognition as sr
from django.db.models import Q
from django.core.mail import send_mail
from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect
from googletrans import Translator
from translate import Translator as trans
from django.views.generic import TemplateView
from django.contrib.auth.models import User


class eng(TemplateView):
    Template_view = "docbot/index.html"
    
    def get(self, request):
        return render(request, self.Template_view, {'english' : True})

    def post(self, request):
        if request.method == 'POST':

            user = request.POST.get('input', False)

            if user:
                res = user
            
            else:


                r = sr.Recognizer()
                print("Please talk")
                with sr.Microphone() as source:
                    # read the audio data from the default microphone
                    audio_data = r.record(source, duration=10)
                    print("Recognizing...")
                    # convert speech to text
                    text = r.recognize_google(audio_data)
                    print("Recognised Speech:" + text)
                    res = text
                
            
            result = get_response(res)
            
            context = {"user": res, "bot": result, 'english' : True}
            return render(request, self.Template_view, context)

    # def get(self, request):
    #     return render(request, self.Template_view)

    # def post(self, request):
    #     if request.method == 'POST':
    #         user = request.POST.get('input', False)
    #         context = {"user": user, "bot": get_response(user)}
    #     return render(request, self.Template_view, context)

@login_required(login_url='customerlogin')
def customer_dashboard_view(request):
    data = User.objects.get(user = request.user)
    dict = {
        'customer': User.objects.get(user_id=request.user.id),
        'dashboard' : True,
        'data' : data,

    }
    

    return render(request, 'customer/customer_dashboard.html', context=dict)


