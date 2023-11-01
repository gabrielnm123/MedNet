from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

def list_perfil(operador):
    return [perfil.name for perfil in operador.groups.all()]

@login_required(login_url='/login/')
def perfil(request):
    perfis = list_perfil(request.user)
    return render(request, 'perfil.html', {'perfis': perfis})
