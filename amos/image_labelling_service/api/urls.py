"""This module contains the URLs exposed by the api subapp."""
from django.urls import path
from .views import add_labels_to_new_city, add_labels_to_existing_city, get_index, get_logs

urlpatterns = [
    path('', get_index, name='get_index'),
    path('cities/logs', get_logs, name='get_logs'),
    path('cities/<city>', add_labels_to_new_city, name='add_labels_to_new_city'),
    path('cities/<city>/existing', add_labels_to_existing_city, name='add_labels_to_existing_city')
]
