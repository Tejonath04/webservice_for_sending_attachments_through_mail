from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello, name='hello'),
    path('sending_mails/', views.sending_mails, name='sending_mails'),
]