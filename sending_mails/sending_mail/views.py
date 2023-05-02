from django.shortcuts import render
from django.http import HttpResponse
import os
import csv
import zipfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


# Create your views here.
def hello(request):
    return HttpResponse('HELLO.........')


def sending_mails(request):
    if request.method == 'POST' and request.POST.get('file'):
        if 'file' in request.POST:
            folder_path = request.POST.get('file')
            Sender_email = request.POST.get('email')
            password = request.POST.get('password')
            Subject = request.POST.get('subject')
        count=0

        # Get the uploaded file
        if not folder_path:
            return HttpResponse('Folder path is required')
            
        if not os.path.isdir(folder_path):
            return HttpResponse('Folder does not exist')
        
        csv_file_path = os.path.join(folder_path, 'main.csv')
        if not os.path.isfile(csv_file_path):
            return HttpResponse('main.csv file not found in the folder')
        
        with open(csv_file_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                attachment_name = row['attachment']
                attachment_path = os.path.join(folder_path, attachment_name)
                email_to = row['mail']
                #return HttpResponse(attachment_path)

                # create a multipart message object and set the email headers
                msg = MIMEMultipart()
                msg['From'] = Sender_email
                msg['To'] = email_to
                msg['Subject'] = Subject

                # attach the file to the email as a MIMEBase object
                with open(attachment_path, 'rb') as attachment:                  
                    part = MIMEBase('application', "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment', filename=attachment_name)
                    msg.attach(part)

                # send the email using the specified SMTP server
                smtp_username = Sender_email
                smtp_password = password
                with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                    smtp.starttls()
                    smtp.login(smtp_username, smtp_password)
                    smtp.sendmail(Sender_email, email_to, msg.as_string())

                    count=count+1

        return HttpResponse(" Mails sent successfully")
    else:
        return render(request, 'display.html')
    