from django.http import request
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Benificial,User, Relatives
from datetime import datetime, timedelta
from functools import wraps
from adminportal.models import Addvaccines
from django.db.models import Q
from adminportal.views import slot_dict
from django.core.mail import send_mail
from django.core.mail import EmailMessage
# Create your views here.

def home(request):
    return render(request, 'home.html')

def is_verified(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        #not a first time user
        if Benificial.objects.filter(user=request.user).exists():
            benificial = Benificial.objects.get(user=request.user)
            #have registered for the vaccine
            if benificial.is_registered:
                if benificial.is_delivered and benificial.slot_timing<=datetime.now():
                    # got vaccinated , for second dose after 80 days
                    if benificial.slot_timing + timedelta(1)<=datetime.now():
                        benificial.slot_timing = None
                        benificial.is_delivered = False
                        benificial.is_registered = False
                        benificial.registration_timing = None
                        benificial.save()
                    else:
                        expiry = benificial.slot_timing.date() + timedelta(1)
                        message = 'wait till '+ expiry.strftime("%d-%b-%Y ") + ' to register again'
                        return render(request,'error.html',{'message':message})
                #slot is not provided or upcoming        
                else:
                    return render(request,'error.html',{'message':'You Are already registered'})
        available_slot = Addvaccines.objects.filter(Q(date__gt=datetime.now())&Q(extra_vaccine__gte=1)).order_by('date').order_by('slot')
        if len(available_slot)==0:
            return render(request,'error.html',{'message':'Sorry, there is no more slots available'})
        return function(request, *args, **kwargs)  
    return wrap
    
    
@login_required(login_url='loginPage')
@is_verified
def register(request):
    roll_number = request.user.last_name
    contact_1 = None
    contact_2 = None
    benificial = None
    try:
        benificial = Benificial.objects.get(user=request.user)
        roll_number = benificial.roll_number
        contact_1 = benificial.contact_1
        contact_2 = benificial.contact_2
    except:
        print("first time")
    if request.method=='POST':
        if benificial is not None:
            benificial.roll_number=request.POST['rollNumber']
            benificial.is_registered=True
            benificial.registration_timing=datetime.now()
            benificial.contact_1=request.POST['contact_1']
            benificial.contact_2=request.POST['contact_2']
            if request.POST['is_second']=="2":
                beneficial.second_dose = True
            benificial.save()
        else:
            second_dose = False
            if request.POST['is_second']=="2":
                second_dose = True
            benificial=Benificial.objects.create(
                user=request.user,
                roll_number=request.POST['rollNumber'],
                is_registered=True,
                registration_timing=datetime.now(),
                contact_1=request.POST['contact_1'],
                contact_2=request.POST['contact_2'],
		second_dose=second_dose
            )
        try: 
            available_slot = Addvaccines.objects.filter(
                Q(date__gt=datetime.now()) & Q(extra_vaccine__gte=1)
            ).order_by('date').order_by('slot')[0]
            benificial.is_delivered=True
            benificial.slot_timing=datetime.combine(available_slot.date,slot_dict[str(available_slot.slot)])
            benificial.save()
            available_slot.extra_vaccine=available_slot.extra_vaccine-1
            available_slot.save()
            s=["9am to 10am", "10am to 11am", "11am to 12 pm", "12 pm to 1 pm", "1pm to 2 pm", "2pm to 3 pm", "3pm to 4pm", "4pm to 5pm"]
            email = EmailMessage(
                subject='Confirmation of Vaccination Slot',
                body="Dear "+request.user.first_name+" ,<br>Your Vaccination slot is scheduled from "+s[int(available_slot.slot)]+" on "+available_slot.date.strftime("%d-%b-%Y")+".Please report at the Covid-19 Vaccination Centre(Day Care Centre, IITG). You are requested to follow social distancing and other COVID protocols at the vaccination centre.<br> Regards,<br>Team SWC",
                from_email='web_swc@iitg.ac.in',
                to=[benificial.user.email],
            )
            email.content_subtype = 'html' 
            try:
                email.send(fail_silently=False)
                return render(request, 'error.html', {'message': 'Registered Successfully'})
            except Exception:
                print(Exception)
                return render(request, 'error.html', {'message': Exception})
        except Exception:
            print(Exception)
            return render(request, 'error.html', {'message': Exception})
    return render(request,'register.html',{'roll_number':roll_number,'contact_1':contact_1,'contact_2':contact_2})

def is_vaccine_available(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        available_slots=Addvaccines.objects.filter(Q(date__gt=datetime.now())&Q(extra_vaccine__gte=1)).order_by('date').order_by('slot')
        if len(available_slots)==0:
            return render(request,'error.html',{'message':'Sorry, there is no more slots available'})
        return function(request, *args, **kwargs)
    return wrap

@login_required(login_url='loginPage')
@is_vaccine_available
def add_relative(request):
    if request.method=='POST':
        second_dose = False
        if request.POST['is_second']=="2":
            second_dose = True
        relative = Relatives.objects.create(
            user=request.user,
            name=request.POST['name'],
            relation=request.POST['relation'],
            contact_1=request.POST['contact_1'],
            contact_2=request.POST['contact_2'],
            is_registered=True,
            registration_timing=datetime.now(),
            second_dose=second_dose,
        )
        try:
            available_slot = Addvaccines.objects.filter(
                Q(date__gt=datetime.now()) & Q(extra_vaccine__gte=1)
            ).order_by('date').order_by('slot')[0]
            relative.slot_timing=datetime.combine(available_slot.date,slot_dict[str(available_slot.slot)])
            relative.save()
            available_slot.extra_vaccine=available_slot.extra_vaccine-1
            available_slot.save()
            s=["9am to 10am", "10am to 11am", "11am to 12 pm", "12 pm to 1 pm", "1pm to 2 pm", "2pm to 3 pm", "3pm to 4pm", "4pm to 5pm"]
            email = EmailMessage(
                subject='Confirmation of Vaccination Slot',
                body="Dear "+relative.name+" "+relative.relation+" of "+request.user.first_name+" ,<br>Your Vaccination slot is scheduled from "+s[int(available_slot.slot)]+" on "+available_slot.date.strftime("%d-%b-%Y")+".Please report at the Covid-19 Vaccination Centre(Day Care Centre, IITG). You are requested to follow social distancing and other COVID protocols at the vaccination centre.<br> Regards,<br>Team SWC",
                from_email='web_swc@iitg.ac.in',
                to=[relative.user.email],
            )
            email.content_subtype = 'html'
            try:
                email.send(fail_silently=False)
                relative.is_delivered=True
                relative.save()
                return render(request, 'error.html', {'message': 'Registered Successfully'})
            except Exception:
                print(Exception)
                return render(request, 'error.html', {'message': 'slot booked but mail was not sent, please contact web_swc@iitg.ac.in'})
        except Exception:
            print(Exception)
            return render(request, 'error.html', {'message': Exception})
    return render(request,'add_relative.html',{'relation':"",'name':"", 'contact_1':"", 'contact_2':""})