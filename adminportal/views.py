from typing import List
from django.db.models.fields import TimeField
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView
from .models import Addvaccines
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import traceback
from django.contrib.admin.views.decorators import staff_member_required
from registration.models import Benificial, User, Relatives
from django.db.models import Q
from datetime import time,datetime
from django.contrib.auth.decorators import login_required

slot_dict = {
    '0': time(9),
    '1': time(10),
    '2': time(11),
    '3': time(12),
    '4': time(13),
    '5': time(14),
    '6': time(15)
}
@staff_member_required
def index(request):
    return render(request,'staff.html', {'slot': slot_dict})
@staff_member_required
def send_email(request):
    if request.method=="POST":
        name = request.POST.get('name')
        slot = request.POST.get('slot')
        doses = request.POST.get('doses')
        date = request.POST.get('date')
        print(name, slot, doses)
        s=["9 to 12", "12 to 3", "3 to 5"]
        benificials = Benificial.objects.filter(
            Q(is_registered=True) & Q(is_delivered=False)
        ).order_by('registration_timing')[:int(doses)]
        print(benificials)
        list_emails = []
        for benificial in benificials:
            benificial.is_delivered=True
            benificial.slot_timing=datetime.combine(datetime.strptime(date,"%Y-%m-%d"),slot_dict[slot])
            benificial.save()   
            list_emails.append(benificial.user.email)
        email = EmailMessage(
            subject='Vaccination Slot Details',
            body="your vaccine slot is "+str(slot_dict[slot])+" "+date,
            from_email='swc@iitg.ac.in',
            to=list_emails,
        )
        Addvaccines.objects.create(
            name_of_vaccine=name,   
            slot=slot,
            date=date,
            numbers_of_vaccine=doses,
            extra_vaccine = int(doses)-len(benificials)
        )
        # 'satyendr@iitg.ac.in'
        email.content_subtype = 'html' 
        try:
            email.send(fail_silently=False)
            return render(request, 'success.html', {'message': 'slot added successfully'})
        except Exception:
            print('errorr')
            # print traceback.format_exc() # you probably want to add a log here instead of console printout
        return render(request, 'success.html', {'message': 'slot added successfully'})

@staff_member_required
def list(request,date,slot_no):
    return render(request,'list.html' , {"benificials":Benificial.objects.filter(slot_timing=datetime.combine(datetime.strptime(date,"%Y-%m-%d"),slot_dict[str(slot_no)])),"relatives":Relatives.objects.filter(slot_timing=datetime.combine(datetime.strptime(date,"%Y-%m-%d"),slot_dict[str(slot_no)]))})

@staff_member_required
def slots_created(request):
    dicti={}
    for slots in Addvaccines.objects.all():
        if slots.date.strftime("%Y-%m-%d") in dicti:
            dicti[slots.date.strftime("%Y-%m-%d")].append(slots.slot)
        else:
            dicti[slots.date.strftime("%Y-%m-%d")]=[slots.slot]
    return render(request,'available_slots.html',{'slots':dicti})

import csv
from django.http import HttpResponse

@staff_member_required
def return_csv(request):
    if request.method != "POST":
       return render(request,'date.html',{})
    response = HttpResponse(content_type='text/csv',headers={'Content-Disposition':'attachment; filename="vaccination_list.csv"'},)
    with open('vaccination_list.csv', 'w') as csvfile:
        writer = csv.writer(response)
        date = request.POST.get('date')
        new_row=[]
        new_row.append("name")
        new_row.append("email")
        new_row.append("roll number/relation")
        new_row.append("slot timing")
        new_row.append("primary contact")
        new_row.append("secondary contact")
        new_row.append("second dose")
        writer.writerow(new_row)
        for obj in Benificial.objects.filter(slot_timing__date=date):
            row = []
            row.append(obj.user.first_name)
            row.append(obj.user.email)
            row.append(obj.roll_number)
            row.append(obj.slot_timing)
            row.append(obj.contact_1)
            row.append(obj.contact_2)
            row.append(obj.second_dose)
            writer.writerow(row)
        for obj in Relatives.objects.filter(slot_timing__date=date):
            row = []
            row.append(obj.name)
            row.append(obj.user.email)
            row.append(obj.relation)
            row.append(obj.slot_timing)
            row.append(obj.contact_1)
            row.append(obj.contact_2)
            row.append(obj.second_dose)
            writer.writerow(row)
    return response
