# from django.shortcuts import render
# from django.http import HttpResponse
# import os
# import csv
# import zipfile
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders

# # Create your views here.
# def hello(request):
#     return HttpResponse('HELLO.........')


# def sending_mails(request):
#     if request.method == 'POST' and request.POST.get('file'):
#         if 'file' in request.POST:
#             folder_path = request.POST.get('file')
#             Sender_email = request.POST.get('email')
#             password = request.POST.get('password')
#             Subject = request.POST.get('subject')
#         count=0

#         # Get the uploaded file
#         if not folder_path:
#             return HttpResponse('Folder path is required')
            
#         if not os.path.isdir(folder_path):
#             return HttpResponse('Folder does not exist')
        
#         csv_file_path = os.path.join(folder_path, 'main.csv')
#         if not os.path.isfile(csv_file_path):
#             return HttpResponse('main.csv file not found in the folder')
        
#         with open(csv_file_path, 'r') as csv_file:
#             reader = csv.DictReader(csv_file)
#             for row in reader:
#                 attachment_name = row['attachment']
#                 attachment_path = os.path.join(folder_path, attachment_name)
#                 email_to = row['mail']
#                 #return HttpResponse(attachment_path)

#                 # create a multipart message object and set the email headers
#                 msg = MIMEMultipart()
#                 msg['From'] = Sender_email
#                 msg['To'] = email_to
#                 msg['Subject'] = Subject

#                 # attach the file to the email as a MIMEBase object
#                 with open(attachment_path, 'rb') as attachment:                  
#                     part = MIMEBase('application', "octet-stream")
#                     part.set_payload(attachment.read())
#                     encoders.encode_base64(part)
#                     part.add_header('Content-Disposition', 'attachment', filename=attachment_name)
#                     msg.attach(part)

#                 # send the email using the specified SMTP server
#                 smtp_username = Sender_email
#                 smtp_password = password
#                 with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
#                     smtp.starttls()
#                     smtp.login(smtp_username, smtp_password)
#                     smtp.sendmail(Sender_email, email_to, msg.as_string())

#                     count=count+1

#         return HttpResponse(" Mails sent successfully")
#     else:
#         return render(request, 'display.html')

import os
import zipfile
import tempfile
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def hello(request):
    return HttpResponse('HELLO.........')

def sending_mails(request):
    if request.method == 'POST' and request.FILES.get('zip_file'):
        zip_file = request.FILES['zip_file']
        Sender_email = request.POST.get('email')
        password = request.POST.get('password')
        Subject = request.POST.get('subject')
        count = 0

        # Create a temporary directory to extract the contents of the zip file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the uploaded zip file to the temporary directory
            zip_file_path = os.path.join(temp_dir, 'uploaded.zip')
            with open(zip_file_path, 'wb') as dest:
                for chunk in zip_file.chunks():
                    dest.write(chunk)

            # Extract the contents of the zip file
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # Look for a folder in the ZIP file (assuming only one folder)
                folder_name = None
                for file_info in zip_ref.infolist():
                    # Check if the file entry represents a folder
                    if '/' in file_info.filename:
                        folder_name = file_info.filename.split('/')[0]
                        break

                if not folder_name:
                    return HttpResponse('No folder found in the ZIP file')

                # Extract the folder
                zip_ref.extractall(temp_dir)

                # Locate the CSV file containing recipient email addresses within the folder
                folder_path = os.path.join(temp_dir, folder_name)
                csv_file_path = os.path.join(folder_path, 'main.csv')
                if not os.path.isfile(csv_file_path):
                    return HttpResponse('recipients.csv file not found in the folder')

                # Read recipient email addresses from the CSV file
                with open(csv_file_path, 'r') as csv_file:
                    reader = csv.DictReader(csv_file)
                    for row in reader:
                        recipient_email = row['mail']
                        attachment_name = row['attachment']
                        attachment_path = os.path.join(folder_path, attachment_name)

                        # Create a multipart message object and set the email headers
                        msg = MIMEMultipart()
                        msg['From'] = Sender_email
                        msg['To'] = recipient_email
                        msg['Subject'] = Subject

                        # Attach the file to the email as a MIMEBase object
                        with open(attachment_path, 'rb') as attachment:
                            part = MIMEBase('application', "octet-stream")
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition', 'attachment', filename=attachment_name)
                            msg.attach(part)

                        # Send the email using the specified SMTP server
                        smtp_username = Sender_email
                        smtp_password = password
                        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                            smtp.starttls()
                            smtp.login(smtp_username, smtp_password)
                            smtp.sendmail(Sender_email, recipient_email, msg.as_string())

                        count += 1

        return HttpResponse(f"{count} mails sent successfully")
    else:
        return render(request, 'display.html')
