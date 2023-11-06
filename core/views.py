from django.shortcuts import render, redirect
from .serializers import PacienteSerializer
from .models import *
from rest_framework import viewsets # fornece uma maneira conveniente de criar views que lidam com ações comuns em um modelo.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib import messages
import pandas as pd
from django.utils.timezone import make_naive

# Create your views here.

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

def get_user_groups(username):
    user = User.objects.get(username=username)
    return ' <hr> '.join([group.name for group in user.groups.all()])

def create_link_operador(row):
    url = r'<a class="ativado" onclick="desativarLink(this)" href="/gerenciar_operador/operador/?usuario='+f'{row["Usuário"]}">'+f'{row["Usuário"]}</a>'
    return url

@user_passes_test(is_member_of('GERENCIAR OPERADOR'), login_url='/perfil')
@login_required(login_url='/login/')
def gerenciar_operador(request):
    operador = request.GET.get('operador')
    usuario = request.GET.get('usuario')
    perfil = request.GET.get('perfil')
    contador = 0
    for valor in (operador, usuario, perfil):
        if not valor:
            contador += 1
    if contador == 2:
        if operador:
            try:
                operadores = User.objects.filter(first_name__icontains=operador)
                if not operadores:
                    operadores = User.objects.all()
                    messages.error(request, 'Operador não Encontrado')
            except:
                operadores = User.objects.all()
        else:
            operadores = User.objects.all()
        if usuario:
            try:
                operadores = User.objects.filter(username__icontains=usuario)
                if not operadores:
                    operadores = User.objects.all()
                    messages.error(request, 'Usuário não Encontrado')
            except:
                operadores = User.objects.all()
        if perfil:
            try:
                operadores = User.objects.filter(groups__name=perfil)
                if not operadores:
                    operadores = User.objects.all()
                    messages.error(request, 'Perfil não Encontrado')
            except:
                operadores = User.objects.all()
        try:
            operadores_df = pd.DataFrame(
                list(operadores.values())
            )
        except:
            operadores_df = pd.DataFrame(
                list(operadores.values())
            ) # essa parte é que filtra
    else:
        operadores = User.objects.all()
        operadores_df = pd.DataFrame(
            list(operadores.values())
        )
        if contador <= 1:
            messages.error(request, 'Preencha Somente um Valor no Formulário')
    try:
        operadores_df = operadores_df[
            operadores_df.is_superuser == False
        ]
        operadores_df = operadores_df[
            operadores_df.is_staff == False
        ]
        operadores_df['Perfil'] = operadores_df['username'].apply(get_user_groups)
        operadores_df.drop(columns=['id', 'password', 'is_superuser', 'last_name', 'is_staff'], inplace=True)
        operadores_df.rename(
            columns={
                'first_name': 'Operador',
                'username': 'Usuário',
                'is_active': 'Operador Ativo',
                'last_login': 'Última Autenticação',
                'date_joined': 'Data de Registro',
                'email': 'Email'
            }, inplace=True
        )
        nova_ordem = ['Usuário', 'Operador', 'Perfil', 'Email', 'Operador Ativo', 'Última Autenticação', 'Data de Registro']
        operadores_df = operadores_df[nova_ordem]
        operadores_df['Operador Ativo'].replace({
            True: 'Sim', False: 'Não'
        }, inplace=True)
        operadores_df['Última Autenticação'] = operadores_df['Última Autenticação'].apply(make_naive)
        operadores_df['Última Autenticação'] = operadores_df['Última Autenticação'].dt.strftime('%d/%m/%Y %H:%M:%S')
        operadores_df['Data de Registro'] = operadores_df['Data de Registro'].apply(make_naive)
        operadores_df['Data de Registro'] = operadores_df['Data de Registro'].dt.strftime('%d/%m/%Y %H:%M:%S')
        operadores_df['Usuário'] = operadores_df.apply(create_link_operador, axis=1)
    except:
        pass
    perfis = Group.objects.all()
    data = {
        'operadores_df': operadores_df.to_html(
            escape=False, index=False
        ),
        'perfis': perfis
    }
    return render(request, 'gerenciar_operador.html', data)
