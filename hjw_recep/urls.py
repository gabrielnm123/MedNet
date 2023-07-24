"""
URL configuration for hjw_recep project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from core import views
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("chaining/", include("smart_selects.urls")), # pra funcionar a biblioteca smart_selects
    path('internacao/', views.internacao),
    path('', RedirectView.as_view(url='/internacao/')), # pra sempre abrir a agenda
    path('login/', views.login_user), # criando a parte de login
    path('login/submit', views.submit_login), # tem que tirar a barra do final se não da erro quando for fazer o post e get
    path('logout/', views.logout_user),
]
