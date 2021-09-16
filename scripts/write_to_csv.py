from registration.models import Benificial
import csv

def run():
    with open('file_name.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        for obj in Benificial.objects.all():
            row = []
            row.append(obj.user.first_name)
            row.append(obj.user.username)
            row.append(obj.roll_number)
            row.append(obj.slot_timing)
            row.append(obj.contact_1)
            row.append(obj.contact_2)
            row.append(obj.second_dose)
            writer.writerow(row)
