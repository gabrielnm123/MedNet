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
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# configurando o rotiador
router = routers.DefaultRouter()
router.register(r'pacientes', views.PacienteViewSet) # Registra um ViewSet chamado PacienteViewSet para o endpoint 'pacientes' usando o método .register(). Isso cria automaticamente as URLs RESTful para as operações CRUD (Create, Read, Update, Delete) relacionadas aos pacientes

urlpatterns = [
    path("admin/", admin.site.urls),
    path('internacao/', views.internacao, name='internacao'),
    path('internacao/paciente/', views.paciente, name='paciente'),
    path('internacao/paciente/visitante/', views.visitante, name='visitante'),
    path('internacao/paciente/visitante/submit', views.submit_visitante, name='submit_visitante'),
    path('', RedirectView.as_view(url='/internacao/')), # pra sempre abrir a internação
    # path('', RedirectView.as_view(url='/admin/')),
    path('login/', views.login_user, name='login'), # criando a parte de login
    path('login/submit', views.submit_login, name='submit_login'), # tem que tirar a barra do final se não da erro quando for fazer o post e get
    path('logout/', views.logout_user, name='logout'),
    path('paciente-autocomplete/', views.PacienteAutocomplete.as_view(), name='paciente-autocomplete'),
    path('api/', include(router.urls), name='api'), # visualizar a api
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
