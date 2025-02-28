from django.urls import path
from . import views

urlpatterns = [
    # path('trigger_confirmations/', views.trigger_confirmations, name='trigger_confirmations'),
    # path('<int:meeting_id>/', views.update_meeting, name='update_meeting'),
    # path('interact_with_meeting/<int:meeting_id>/', views.interact_with_meeting, name='interact_with_meeting'),


    path('start_agent/', views.start_agent, name='start_agent'),
    path('handle_response/', views.handle_response, name='handle_response'),



]