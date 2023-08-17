from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from dal import autocomplete
from core.models import *
from django.http.response import Http404
import json

# Create your views here.

def login_user(request):
    return render(request, 'login.html') # abrir a pagina login.html

def submit_login(request):
    if request.POST: # se a requisição for do tipo POST é verdadeiro
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect ('/') # quando autenticado volta por indice que vai pra agenda que verifica que esta autenticado e mostrar o conteudo
        else:
            messages.error(request, 'Usuário ou senha inválido') # se der erro no login, da uma mensagem de erro no html login
    return redirect('/') # independente se for um post ou não sempre vai direcionar pra pagina inicial

def logout_user(request):
    logout(request)
    return redirect('/')

@login_required(login_url='/login/')
def internacao(request):
    search_term = request.GET.get('search')

    if search_term:
        pacientes = Paciente.objects.filter(paciente__icontains=search_term)
    else:
        pacientes = None

    return render(request, 'internacao.html', {'pacientes': pacientes})

def paciente(request):
    id_paciente = request.GET.get('id')
    dados = {}
    if id_paciente:
        try:
            dados['paciente'] = Paciente.objects.get(id=id_paciente)
        except Exception:
            raise Http404()
    return render(request, 'paciente.html', dados)

class PacienteAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Paciente.objects.all()
        if self.q:
            qs = qs.filter(paciente__icontains=self.q)  # Corrigindo o filtro para o campo 'paciente'
        return qs

def my_view(request):
    return render(request, 'my_template.html')
    