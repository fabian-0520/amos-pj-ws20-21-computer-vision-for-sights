from django.urls import path

from . import views

urlpatterns = [
    path('image/<city>', views.persist_sight_image, name='persist_sight_image'),
    path('model/<city>', views.get_trained_city_model, name='get_trained_city_model'),
    path('cities', views.get_supported_cities, name='get_supported_cities'),
    path('', views.get_index, name='get_index'),
]
