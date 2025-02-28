from django.urls import path
from . import views

urlpatterns = [
    path('conversation/', views.conversation_view, name='conversation'),
    path('invoke/', views.invoke_view, name='invoke'),
]