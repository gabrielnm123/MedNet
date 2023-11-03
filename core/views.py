from django.shortcuts import render, redirect
from dal import autocomplete
from .serializers import PacienteSerializer
from .models import *
from rest_framework import viewsets # fornece uma maneira conveniente de criar views que lidam com ações comuns em um modelo.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

class PacienteAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Paciente.objects.all()
        if self.q:
            qs = qs.filter(nome__icontains=self.q)  # Corrigindo o filtro para o campo 'paciente'
        return qs

class PacienteViewSet(viewsets.ModelViewSet): # classe será uma subclasse de ModelViewSet, que já possui funcionalidades predefinidas para lidar com operações CRUD (Create, Retrieve, Update, Delete) em um modelo.
    queryset = Paciente.objects.all() # Define o queryset (conjunto de objetos do banco de dados) que será usado para a visualização. Neste caso, todos os objetos do modelo Paciente são recuperados.
    serializer_class = PacienteSerializer # Define a classe de serializer que será usada para serializar e desserializar os objetos Paciente. O serializer é responsável por converter os objetos em dados JSON (ou outros formatos) e vice-versa.

def is_member(operador, perfil_name):
    return operador.groups.filter(name=perfil_name).exists()

def is_member_of(perfil_name):
    return lambda operador: is_member(operador, perfil_name)

def login_user(request):
    if request.user.is_authenticated:
        return redirect('/recepcao_principal')
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

def list_perfil(operador):
    return [perfil.name for perfil in operador.groups.all()]

@login_required(login_url='/login/')
def perfil(request):
    perfis = list_perfil(request.user)
    return render(request, 'perfil.html', {'perfis': perfis})
