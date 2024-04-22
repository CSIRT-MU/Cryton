"""cryton.hive URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic.base import RedirectView

from cryton.hive.config.settings import SETTINGS

urlpatterns = [
    path(SETTINGS.api.root, include("cryton.hive.cryton_app.urls")),
    path("admin/", admin.site.urls),
    re_path(r"^|doc/$", RedirectView.as_view(pattern_name="swagger-ui", permanent=False)),
    path("redoc/", RedirectView.as_view(pattern_name="redoc-ui", permanent=False)),
]
