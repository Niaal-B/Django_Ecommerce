from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('list/', views.message_list, name='message_list'),
    path('reply/<int:message_id>/', views.reply_message, name='reply_message'),
]
