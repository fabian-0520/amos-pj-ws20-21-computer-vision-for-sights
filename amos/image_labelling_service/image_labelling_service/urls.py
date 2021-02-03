"""image_labelling_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.conf.urls.static import static
from django.urls import path, include
from swagger_render.views import SwaggerUIView

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./auth.json")  # path to included Google Vision API credentials

urlpatterns = [
    path("api/", include("api.urls")),  # for backwards compatibility with the data mart refresher
    path("swagger/", SwaggerUIView.as_view()),
] + static("/docs/", document_root="docs")
