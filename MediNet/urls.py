"""
URL configuration for MediNet project.

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
from recepcao_principal import views
from django.views.generic import RedirectView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# configurando o rotiador
router = routers.DefaultRouter()
router.register(r'pacientes', views.PacienteViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recepcao_principal/', views.recepcao_principal, name='recepcao_principal'),
    path('recepcao_principal/censo_visitante/', views.censo_visitante, name='censo_visitante'),
    path('recepcao_principal/paciente/', views.paciente, name='paciente'),
    path('recepcao_principal/paciente/comunicado_interno/', views.comunicado_interno, name='comunicado_interno'),
    path('recepcao_principal/paciente/comunicado_interno/submit', views.submit_ci, name='submit_ci'),
    path('recepcao_principal/paciente/visitante/', views.visitante, name='visitante'),
    path('recepcao_principal/paciente/visitante/submit', views.submit_visitante, name='submit_visitante'),
    path('recepcao_principal/paciente/visitante/delete', views.delete_visitante, name='delete_visitante'),
    path('', RedirectView.as_view(url='/recepcao_principal/')), # pra sempre abrir a internação
    # path('', RedirectView.as_view(url='/admin/')),
    path('login/', views.login_user, name='login'), # criando a parte de login
    path('login/submit', views.submit_login, name='submit_login'), # tem que tirar a barra do final se não da erro quando for fazer o post e get
    path('logout/', views.logout_user, name='logout'),
    path('paciente-autocomplete/', views.PacienteAutocomplete.as_view(), name='paciente-autocomplete'),
    path('api/', include(router.urls), name='api'), # visualizar a api
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
