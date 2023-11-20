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
from protonmail import ProtonMail
import os
from dotenv import load_dotenv
import random
import string

# Create your views here.

load_dotenv()

class PacienteViewSet(viewsets.ModelViewSet): # classe será uma subclasse de ModelViewSet, que já possui funcionalidades predefinidas para lidar com operações CRUD (Create, Retrieve, Update, Delete) em um modelo.
    queryset = Paciente.objects.all() # Define o queryset (conjunto de objetos do banco de dados) que será usado para a visualização. Neste caso, todos os objetos do modelo Paciente são recuperados.
    serializer_class = PacienteSerializer # Define a classe de serializer que será usada para serializar e desserializar os objetos Paciente. O serializer é responsável por converter os objetos em dados JSON (ou outros formatos) e vice-versa.

def is_member(operador, perfil_name):
    return operador.groups.filter(name=perfil_name).exists()

def is_member_of(perfil_name):
    return lambda operador: is_member(operador, perfil_name)

def login_user(request):
    if request.user.is_authenticated:
        return redirect('/perfil/')
    return render(request, 'login.html') # abrir a pagina login.html

def submit_login(request):
    if 'login' in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect ('/') # quando autenticado volta por indice que vai pra agenda que verifica que esta autenticado e mostrar o conteudo
        else:
            messages.error(request, 'USUÁRIO E/OU SENHA INVALIDO(S)') # se der erro no login, da uma mensagem de erro no html login
        return redirect('/') # independente se for um post ou não sempre vai direcionar pra pagina inicial
    else:
        username = request.POST.get('username')
        return redirect(f'/login/mudar_senha/?esqueci_senha=sim&usuario={username}')
        
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
                    messages.error(request, 'OPERADOR NÃO ENCONTRADO')
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
                messages.error(request, 'USUÁRIO NÃO ENCONTRADO')
        if perfil:
            try:
                operadores = User.objects.filter(groups__name=perfil)
            except:
                messages.error(request, 'PERFIL NÃO ENCONTRADO')
        if operador_ativo:
            try:
                if operador_ativo == 'True':
                    operadores = User.objects.filter(is_active=True)
                else:
                    operadores = User.objects.filter(is_active=False)
            except:
                if operador_ativo == 'True':
                    messages.error(request, 'NÃO ENCONTRADO OPERADORES ATIVOS')
                else:
                    messages.error(request, 'NÃO ENCONTRADO OPERADORES DESATIVADOS')
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
        messages.error(request, 'PREENCHA SOMENTE COM UM VALOR O FORMULÁRIO')
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
                messages.error(request, 'EMAIL INVALIDO')
                return redirect(f'/gerenciar_operador/operador/?usuario={usuario}')
            if not usuario_novo.isnumeric() or len(usuario_novo) != 11:
                messages.error(request, 'USUÁRIO DEVE SER CPF DO OPERADOR')
                return redirect(f'/gerenciar_operador/operador/?usuario={usuario}')
            if len(senha) < 11:
                messages.error(request, 'SENHA PEQUENA, MINIMO 11 CARACTÉRES')
                return redirect(f'/gerenciar_operador/operador/?usuario={usuario}')
            if senha != repetir_senha:
                messages.error(request, 'CONFIRMAÇÃO DE SENHA INCORRETA')
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
                messages.success(request, 'ALTERAÇÃO NO OPERADOR FEITA COM SUCESSO')
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
                messages.success(request, 'OPERADOR CRIADO COM SUCESSO')
    except:
        messages.error(request, 'PREENCHA CORRETAMENTE O FORMULÁRIO')
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

@login_required(login_url='/login/')
def submit_mudar_senha(request):
    try:
        if request.POST:
            esqueci_senha = request.POST.get('esqueci_senha')
            if esqueci_senha != 'sim':
                senha_atual = request.POST.get('senha_atual')
                nova_senha = request.POST.get('nova_senha')
                repetir_nova_senha = request.POST.get('repetir_nova_senha')
                if request.user.check_password(senha_atual):
                    if nova_senha == repetir_nova_senha:
                        if len(nova_senha) < 11:
                            messages.error(request, 'A NOVA SENHA DEVE TER, NO MÍNIMO, 11 CARACTÉRES')
                            return redirect('/perfil/mudar_senha')
                        else:
                            request.user.set_password(nova_senha)
                            request.user.save()
                            messages.success(request, 'SENHA TROCADA COM SUCESSO')
                            login(request, request.user)
                    else:
                        messages.error(request, 'REPITA A SENHA CORRETAMENTE')
                        return redirect('/perfil/mudar_senha')
                else:
                    messages.error(request, 'SENHA ATUAL INCORRETA')
                    return redirect('/perfil/mudar_senha')
    except:
        messages.error(request, 'PREENCHA CORRETAMENTE O FORMULÁRIO')
        return redirect('/perfil/mudar_senha')
    return redirect('/perfil/')

@login_required(login_url='/login/')
def mudar_senha(request):
    return render(request, 'mudar_senha.html')

def submit_mudar_senha_esqueci(request):
    try:
        if request.POST:
            esqueci_senha = request.POST.get('esqueci_senha')
            if esqueci_senha == 'sim':
                usuario = request.POST.get('usuario')
                code = request.POST.get('code')
                codigo = request.POST.get('codigo').strip()
                nova_senha = request.POST.get('nova_senha').strip()
                repetir_nova_senha = request.POST.get('repetir_nova_senha').strip()
                if nova_senha == repetir_nova_senha:
                    if len(nova_senha) < 11:
                        messages.error(request, 'A NOVA SENHA DEVE TER, NO MÍNIMO, 11 CARACTÉRES')
                        return redirect(f'/login/mudar_senha/?esqueci_senha=sim&usuario={usuario}')
                    elif codigo == code:
                        operador = User.objects.get(username=usuario)
                        operador.set_password(nova_senha)
                        operador.save()
                        messages.success(request, 'SENHA TROCADA COM SUCESSO')
                        login(request, operador)
                    else:
                        messages.error(request, 'CÓDIGO NÃO É O MESMO ENVIADO PARA O EMAIL DO OPERADOR')
                        return redirect(f'/login/mudar_senha/?esqueci_senha=sim&usuario={usuario}')
                else:
                        messages.error(request, 'REPITA A SENHA CORRETAMENTE')
                        return redirect(f'/login/mudar_senha/?esqueci_senha=sim&usuario={usuario}')
    except:
        messages.error(request, 'PREENCHA CORRETAMENTE O FORMULÁRIO')
        return redirect(f'/login/mudar_senha/?esqueci_senha=sim&usuario={usuario}')
    return redirect('/')

def mudar_senha_esqueci(request):
    esqueci_senha = request.GET.get('esqueci_senha')
    usuario = request.GET.get('usuario')

    try:
        if not usuario:
            messages.error(request, 'FORNEÇA UM USUÁRIO PRA PODER MUDAR A SENHA')
            return redirect('/')
        elif esqueci_senha == 'sim':
            username = os.environ.get('USERNAME')
            password = os.environ.get('PASSWORD')

            proton = ProtonMail()
            proton.login(username, password)

            private_key = os.environ.get('PRIVATE_KEY')
            passphrase = os.environ.get('PASSPHRASE')
            proton.pgp_import(private_key, passphrase=passphrase)



            recipients = [User.objects.get(username=usuario).email]
            subject = 'Não Responda'
            code = ''.join(random.choice(string.ascii_letters + string.digits) for contador in range(10))
            with open('msg.html', 'r') as file:
                body = file.read().replace('code', code)

            new_message = proton.create_message(
                recipients=recipients,
                subject=subject,
                body=body
            )

            try:
                proton.send_message(new_message)
            except:
                pass
            messages.info(request, f'O CÓDIGO FOI ENVIADO DO EMAIL {username.upper()} PARA O EMAIL CADASTRADO DO OPERADOR, SE NÃO FOI ENVIADO FALE COM A GERENCIA DO SEU SETOR')
            data = {
                'esqueci_senha': esqueci_senha,
                'usuario': usuario,
                'code': code
            }
    except Exception as error:
        messages.error(request, error)
        return redirect('/')
    return render(request, 'mudar_senha.html', data)
