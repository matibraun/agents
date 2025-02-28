from django.urls import path

from .views.supervisor import whatsapp_response
from .views.meeting_notification import MeetingNotificationView

urlpatterns = [
    path('meeting-notifications/', MeetingNotificationView.as_view(), name='meeting-notifications'),
    path("whatsapp-response/", whatsapp_response, name="whatsapp-response"),
]