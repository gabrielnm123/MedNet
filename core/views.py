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
from validate_email import validate_email

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
    operador_ativo = request.GET.get('operador_ativo')
    contador = 0
    for valor in (operador, usuario, perfil, operador_ativo):
        if valor:
            contador += 1
    if contador <= 1:
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
                    del(operadores)
                    raise ValueError()
            except:
                messages.error(request, 'Usuário não Encontrado')
        if perfil:
            try:
                operadores = User.objects.filter(groups__name=perfil)
            except:
                messages.error(request, 'Perfil não Encontrado')
        if operador_ativo:
            try:
                if operador_ativo == 'True':
                    operadores = User.objects.filter(is_active=True)
                else:
                    operadores = User.objects.filter(is_active=False)
            except:
                if operador_ativo == 'True':
                    messages.error(request, 'Não Encontrado Operadores Ativos')
                else:
                    messages.error(request, 'Não Encontrado Operadores Desativados')
        try:
            operadores_df = pd.DataFrame(
                list(operadores.values())
            )
        except:
            try:
                operadores_df = pd.DataFrame(
                    {
                        'Usuário': [r'<a class="ativado" onclick="desativarLink(this)" href="/gerenciar_operador/operador/?usuario='+f'{operadores.username}">'+f'{operadores.username}</a>'],
                        'Operador': [operadores.first_name],
                        'Perfil': [' <hr> '.join([group.name for group in operadores.groups.all()])],
                        'Email': [operadores.email],
                        'Operador Ativo': [operadores.is_active],
                        'Última Autenticação': [operadores.last_login],
                        'Data de Registro': [operadores.date_joined]
                    }
                )
            except:
                operadores = User.objects.all()
                operadores_df = pd.DataFrame(
                    list(operadores.values())
                )
    else:
        operadores = User.objects.all()
        operadores_df = pd.DataFrame(
            list(operadores.values())
        )
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
        operadores_df['Última Autenticação'] = operadores_df['Última Autenticação'].apply(
            lambda x: make_naive(x).strftime('%d/%m/%Y %H:%M:%S') if pd.notnull(x) else 'Nunca'
        ) # estudar sobre lambda
        operadores_df['Data de Registro'] = operadores_df['Data de Registro'].apply(make_naive)
        operadores_df['Data de Registro'] = operadores_df['Data de Registro'].dt.strftime('%d/%m/%Y %H:%M:%S')
        operadores_df['Usuário'] = operadores_df.apply(create_link_operador, axis=1)
    except:
        operadores_df['Usuário'] = list()
        operadores_df['Operador'] = list()
        operadores_df['Perfil'] = list()
        operadores_df['Email'] = list()
        operadores_df['Operador Ativo'] = list()
        operadores_df['Última Autenticação'] = list()
        operadores_df['Data de Registro'] = list()
    perfis = Group.objects.all()
    data = {
        'operadores_df': operadores_df.to_html(
            escape=False, index=False
        ),
        'perfis': perfis,
        'operador': operador,
        'usuario': usuario,
        'perfil': perfil,
        'operador_ativo': operador_ativo
    }
    return render(request, 'gerenciar_operador.html', data)

@user_passes_test(is_member_of('GERENCIAR OPERADOR'), login_url='/perfil')
@login_required(login_url='/login/')
def submit_operador(request):
    try:
        if request.POST:
            usuario = request.POST.get('usuario')
            usuario_novo = request.POST.get('usuario_novo')
            senha = request.POST.get('senha')
            repetir_senha = request.POST.get('repetir-senha')
            nome = request.POST.get('nome').strip().upper()
            email = request.POST.get('email')
            perfis = request.POST.getlist('perfil')
            ativo = request.POST.get('ativo')
            if not validate_email(email):
                messages.error(request, 'Email Invalido')
                return redirect(f'/gerenciar_operador/operador/?usuario={usuario}')
            if not usuario_novo.isnumeric() or len(usuario_novo) != 11:
                messages.error(request, 'Usuário Deve ser o CPF')
                return redirect(f'/gerenciar_operador/operador/?usuario={usuario}')
            if len(senha) < 11:
                messages.error(request, 'Senha Pequena, Minimo 11 Caractéres')
                return redirect(f'/gerenciar_operador/operador/?usuario={usuario}')
            if senha != repetir_senha:
                messages.error(request, 'Confirmação de Senha Incorreta')
                return redirect(f'/gerenciar_operador/operador/?usuario={usuario}')
            if usuario:
                operador = User.objects.get(username=usuario)
                if operador.username != usuario_novo != '':
                    operador.username = usuario_novo
                if senha != '' and not operador.check_password(senha):
                    operador.set_password(senha)
                if operador.first_name != nome != '':
                    operador.first_name = nome
                if operador.email != email != '':
                    operador.email = email
                for perfil in perfis:
                    if perfil not in [group.name for group in operador.groups.all()]:
                        operador.groups.add(Group.objects.get(name=perfil))
                for perfil in [group.name for group in operador.groups.all()]:
                    if perfil not in perfis:
                        operador.groups.remove(Group.objects.get(name=perfil))
                if ativo == None and operador.is_active:
                    operador.is_active = False
                else:
                    operador.is_active = True
                operador.save()
            else:
                operador = User.objects.create(
                    username=usuario_novo,
                    first_name=nome,
                    email=email,
                    is_active=True
                )
                operador.groups.add(*[Group.objects.get(name=perfil) for perfil in perfis])
                operador = User.objects.get(username=usuario_novo)
                operador.set_password(senha)
                operador.save()
    except:
        messages.error(request, 'Preencha Corretamente o Formulário')
        return redirect(f'/gerenciar_operador/operador/?usuario={usuario}')
    return redirect(f'/gerenciar_operador/operador/?usuario={usuario_novo}')

@user_passes_test(is_member_of('GERENCIAR OPERADOR'), login_url='/perfil')
@login_required(login_url='/login/')
def operador(request):
    usuario = request.GET.get('usuario')
    perfis = Group.objects.all()
    if usuario:
        try:
            operador = User.objects.get(username=usuario)
        except:
            messages.error(request, '')
        data = {
            'perfis': perfis,
            'operador': operador,
            'new': False
        }
    else:
        data = {
            'perfis': perfis,
            'new': True
        }
    return render(request, 'operador.html', data)
