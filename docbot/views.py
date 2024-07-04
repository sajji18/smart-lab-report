from django.shortcuts import render, redirect, reverse
from authentication.models import User
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, JsonResponse
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
from docAI.models import Message


def get_messages(request):
    messages = request.session.get('messages', [])
    return JsonResponse({'messages': messages})


class customer_chatbot_view(TemplateView):
    template_name = 'docbot/customer_chatbot.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add or override context data here
        context['english'] = True
        return context

    def post(self, request):
        if self.request.method == 'POST':
            user = self.request.POST.get('content', False)
            print(user)
            if not user:
                r = sr.Recognizer()
                print("Please talk")
                with sr.Microphone() as source:
                    # read the audio data from the default microphone
                    audio_data = r.record(source, duration=10)
                    print("Recognizing...")
                    # convert speech to text
                    try:
                        user = r.recognize_google(audio_data)
                    except sr.UnknownValueError:
                        print("Google Speech Recognition could not understand audio")
                    except sr.RequestError as e:
                        print("Could not request results from Google Speech Recognition service; {0}".format(e))
                    print("Recognised Speech:")

            result = get_response(user)
            print(result)
            
            messages = request.session.get('messages', [])
            messages.append({'sender': 'user', 'content': user})
            messages.append({'sender': 'bot', 'content': result})
            request.session['messages'] = messages
            return JsonResponse({'result': result})
        else:
            messages = request.session.get('messages', [])
            context = {'messages': messages}
            return render(request, 'docbot/customer_chatbot.html', context)


    # def get(self, request):
    #     return render(request, self.Template_view)

    # def post(self, request):
    #     if request.method == 'POST':
    #         user = request.POST.get('input', False)
    #         context = {"user": user, "bot": get_response(user)}
    #     return render(request, self.Template_view, context)

# @login_required(login_url='customerlogin')
# def customer_dashboard_view(request):
#     data = User.objects.get(user = request.user)
#     dict = {
#         'customer': User.objects.get(user_id=request.user.id),
#         'dashboard' : True,
#         'data' : data,

#     }

#     return render(request, 'docAI/customer_dashboard.html', context=dict)


# @login_required
# def customer_chatbot_view (request):
#     return render(request, 'docAI/customer_chatbot.html')


