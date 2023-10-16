from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from dal import autocomplete
from .models import *
from django.http.response import Http404
from rest_framework import viewsets # fornece uma maneira conveniente de criar views que lidam com ações comuns em um modelo.
from .serializers import PacienteSerializer
import pandas as pd
from django.utils.timezone import make_naive, localtime, now
from datetime import datetime

# Create your views here.

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

@login_required(login_url='/login/')
def delete_visitante(prontuario, visitante_id):
    visitante = Visitante.objects.get(id=visitante_id)
    visitante.delete()
    return redirect(f'/recepcao_principal/paciente/visitante?prontuario={prontuario}')

def create_link_paciente(row):
    url = r'<a class="ativado" onclick="desativarLink(this)" href="/recepcao_principal/paciente/?prontuario='+f'{row["prontuario"]}">'+f'{row["nome"]}</a>'
    return url

@login_required(login_url='/login/')
def recepcao_principal(request):
    paciente = request.GET.get('paciente')
    prontuario = request.GET.get('prontuario')
    visitante = request.GET.get('visitante')
    contador = 0
    for valor in (paciente, prontuario, visitante):
        if not valor:
            contador += 1
    if contador == 2:
        if paciente:
            try:
                pacientes = Paciente.objects.filter(nome__icontains=paciente)
                if not pacientes:
                    pacientes = Paciente.objects.all()
                    messages.error(request, 'Paciente não Encontrado')
            except:
                pacientes = Paciente.objects.all()
        else:
            pacientes = Paciente.objects.all()
        if prontuario:
            try:
                pacientes = Paciente.objects.get(prontuario=prontuario)
            except:
                messages.error(request, 'Prontuário não Encontrado')
                pass
        if visitante:
            try:
                visitantes = list(Visitante.objects.filter(nome__icontains=visitante).values())
                prontuarios = list()
                for objetos in visitantes:
                    for key, value in objetos.items():
                        if key == 'paciente_id':
                            prontuarios.append(value)
                prontuarios = list(set(prontuarios))
                pacientes = Paciente.objects.filter(prontuario__in=prontuarios)
                if not pacientes:
                    pacientes = Paciente.objects.all()
                    messages.error(request, 'Visitante não Encontrado')
            except:
                pass
        try:
            pacientes_df = pd.DataFrame(
                list(pacientes.values())
            )
        except:
            pacientes_df = pd.DataFrame(
                {
                    'prontuario': [pacientes.prontuario],
                    'nome': [pacientes.nome],
                    'clinica': [pacientes.clinica],
                    'leito': [pacientes.leito],
                    'comunicado_interno': [pacientes.comunicado_interno],
                    'internado': [pacientes.internado],
                    'data_registro': [pacientes.data_registro]
                }
            )
    else:
        pacientes = Paciente.objects.all()
        pacientes_df = pd.DataFrame(
            list(pacientes.values())
        )
        if contador <= 1:
            messages.error(request, 'Preencha Somente um Valor no Formulário')
    try:
        pacientes_df['data_registro'] = pacientes_df['data_registro'].apply(make_naive)
        pacientes_df['data_registro'] = pacientes_df['data_registro'].dt.strftime('%d/%m/%Y %H:%M:%S')
        pacientes_df['nome'] = pacientes_df.apply(create_link_paciente, axis=1)
        pacientes_df = pacientes_df[
            pacientes_df.internado == True
        ]
        pacientes_df.drop(columns=['comunicado_interno', 'prontuario', 'internado'], inplace=True)
        pacientes_df.rename(
            columns={
                'nome': 'Paciente',
                'clinica': 'Clínica',
                'leito': 'Leito',
                'data_registro': 'Data de Registro'
            }, inplace=True
        )
    except:
        pacientes_df['Paciente'] = list()
        pacientes_df['Clínica'] = list()
        pacientes_df['Leito'] = list()
        pacientes_df['Data de Registro'] = list()
    pacientes_df = pacientes_df.to_html(
        escape=False, index=False
    )
    data = {
        'pacientes_df': pacientes_df,
        'paciente': paciente,
        'prontuario': prontuario,
        'visitante': visitante
    }
    return render(request, 'recepcao_principal.html', data)

@login_required(login_url='/login/')
def paciente(request):
    prontuario = request.GET.get('prontuario')
    dados = {}
    dados['prontuario'] = prontuario
    if prontuario:
        try:
            dados['paciente'] = Paciente.objects.get(prontuario=prontuario)
        except Exception:
            raise Http404()
    return render(request, 'paciente.html', dados)

def create_link_autocomplete_visitante(row):
    url = r'<a class="ativado" onclick="desativarLink(this)" href="/recepcao_principal/paciente/visitante?prontuario='+f'{row["paciente_id"]}'+'&visitante_id='+f'{row["id"]}"'+r'>'+f'{row["nome"]}'+r'</a>'
    return url

def create_link_delete_visitante(row):
    url = r'<a class="ativado" onclick="desativarLink(this)" href="/recepcao_principal/paciente/visitante/delete?prontuario='+f'{row["paciente_id"]}'+'&visitante_id='+f'{row["id"]}"'+r'>'+f'{row["Excluir Visitante"]}'+r'</a>'
    return url

def create_visualization_parentesco_visitante(row):
    parentesco = Parentesco.objects.get(id=row['parentesco_id'])
    return parentesco

def create_visualization_operador(row):
    operador = User.objects.get(id=row['operador_id'])
    return operador.first_name

@login_required(login_url='/login/')
def delete_visitante(request):
    prontuario = request.GET.get('prontuario')
    visitante_id = request.GET.get('visitante_id')
    try:
        visitante = Visitante.objects.get(id=visitante_id)
        visitante.delete()
    except Exception:
        raise Http404()
    return redirect(f'/recepcao_principal/paciente/visitante?prontuario={prontuario}')

@login_required(login_url='/login/')
def visitante(request):
    prontuario = request.GET.get('prontuario')
    visitante_id = request.GET.get('visitante_id')
    dados = {}
    dados['prontuario'] = prontuario
    if prontuario:
        try:
            dados['paciente'] = Paciente.objects.get(prontuario=prontuario)
            if Visitante.objects.filter(paciente__prontuario=prontuario).values():
                visitantes_df = pd.DataFrame(list(
                    Visitante.objects.filter(paciente__prontuario=prontuario).values()
                ))
                visitantes_df['data_registro'] = visitantes_df['data_registro'].apply(make_naive)
                visitantes_df['data_registro'] = visitantes_df['data_registro'].dt.strftime('%d/%m/%Y %H:%M:%S')
                visitantes_df = visitantes_df[::-1]
                visitantes_df['Excluir Visitante'] = 'Excluir'
                visitantes_df['Excluir Visitante'] = visitantes_df.apply(create_link_delete_visitante, axis=1)
                visitantes_df['nome'] = visitantes_df.apply(create_link_autocomplete_visitante, axis=1)
                visitantes_df['parentesco_id'] = visitantes_df.apply(create_visualization_parentesco_visitante, axis=1)
                visitantes_df['operador_id'] = visitantes_df.apply(create_visualization_operador, axis=1)
                visitantes_df.rename(
                    columns={
                        'data_registro': 'Data de Registro',
                        'nome': 'Visitante',
                        'parentesco_id': 'Parentesco',
                        'documento': 'Documento',
                        'operador_id': 'Operador',
                    }, inplace=True
                )
                visitantes_df.drop(columns=['id', 'paciente_id', 'clinica', 'leito'], inplace=True)
                dados['visitantes_df'] = visitantes_df.to_html(
                    escape=False, index=False
                )
        except Exception:
            raise Http404()
    if visitante_id:
        try:
            dados['visitante'] = Visitante.objects.get(id=visitante_id)
        except Exception:
            raise Http404()
    dados['parentescos'] = Parentesco.objects.all()
    dados['boolean_visitante'] = True
    return render(request, 'visitante.html', dados)

@login_required(login_url='/login/')
def submit_visitante(request):
    try:
        if request.POST:
            prontuario = int(request.POST.get('prontuario'))
            paciente = Paciente.objects.get(prontuario=prontuario)
            comunicado_interno = request.POST.get('comunicado_interno')
            if paciente.comunicado_interno != comunicado_interno:
                paciente.comunicado_interno = comunicado_interno
            nome = request.POST.get('nome')
            try:
                parentesco = Parentesco.objects.get(tipo=request.POST.get('parentesco'))
            except:
                raise Exception()
            documento = request.POST.get('documento')
            if nome.strip() == '':
                raise Exception()
            if documento.strip() == '':
                raise Exception()
            Visitante.objects.create(
                paciente=paciente,
                nome=nome,
                parentesco=parentesco,
                documento=documento,
                operador=request.user
            )
    except Exception as error:
        messages.error(request, 'Preencha Corretamente o Formulário')
    return redirect(f'/recepcao_principal/paciente/visitante/?prontuario={prontuario}')

@login_required(login_url='/login/')
def comunicado_interno(request):
    prontuario = request.GET.get('prontuario')
    dados = {}
    dados['prontuario'] = prontuario
    if prontuario:
        try:
            dados['paciente'] = Paciente.objects.get(prontuario=prontuario)
            dados['boolean_comunicado_interno'] = True
        except Exception:
            raise Http404()
    return render(request, 'comunicado_interno.html', dados)

@login_required(login_url='/login/')
def submit_ci(request):
    try:
        if request.POST:
            prontuario = int(request.POST.get('prontuario'))
            comunicado_interno = request.POST.get('comunicado_interno')
            paciente = Paciente.objects.get(prontuario=prontuario)
            if paciente.comunicado_interno != comunicado_interno:
                paciente.comunicado_interno = comunicado_interno
                paciente.save()
    except:
        messages.error(request, 'Preencha o Formulário do Visitante')
    return redirect(f'/recepcao_principal/paciente/?prontuario={prontuario}')

def create_visualization_paciente(row):
    paciente = Paciente.objects.get(prontuario=row['paciente_id'])
    return paciente

@login_required(login_url='/login/')
def censo_visitante(request):
    data_registro = request.GET.get('data_registro')
    hoje = localtime(now()).date().isoformat()
    if data_registro:
        try:
            search_date = datetime.strptime(data_registro, r'%Y-%m-%d').date()
            visitantes = Visitante.objects.filter(data_registro__date=search_date)
            visitantes_df = pd.DataFrame(
                list(visitantes.values())
            )
            visitantes_df['data_registro'] = visitantes_df['data_registro'].apply(make_naive)
            visitantes_df['data_registro'] = visitantes_df['data_registro'].dt.strftime('%d/%m/%Y %H:%M:%S')
            visitantes_df = visitantes_df[::-1]
            visitantes_df['parentesco_id'] = visitantes_df.apply(create_visualization_parentesco_visitante, axis=1)
            visitantes_df['operador_id'] = visitantes_df.apply(create_visualization_operador, axis=1)
            visitantes_df['paciente_id'] = visitantes_df.apply(create_visualization_paciente, axis=1)
            visitantes_df.rename(
                columns={
                    'data_registro': 'Data de Registro',
                    'paciente_id': 'Paciente',
                    'clinica': 'Clínica',
                    'leito': 'Leito',
                    'nome': 'Visitante',
                    'parentesco_id': 'Parentesco',
                    'documento': 'Documento',
                    'operador_id': 'Operador',
                }, inplace=True
            )
            visitantes_df.drop(columns='id', inplace=True)
            visitantes_df = visitantes_df.to_html(
                escape=False, index=False, classes='censo_visitante_dataframe'
            )
        except:
            visitantes_df = None
            data_registro = hoje
    else:
        visitantes_df = None
        data_registro = hoje
    return render(request, 'censo_visitante.html', {'visitantes_df': visitantes_df, 'data_registro': data_registro})

class PacienteAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Paciente.objects.all()
        if self.q:
            qs = qs.filter(nome__icontains=self.q)  # Corrigindo o filtro para o campo 'paciente'
        return qs

class PacienteViewSet(viewsets.ModelViewSet): # classe será uma subclasse de ModelViewSet, que já possui funcionalidades predefinidas para lidar com operações CRUD (Create, Retrieve, Update, Delete) em um modelo.
    queryset = Paciente.objects.all() # Define o queryset (conjunto de objetos do banco de dados) que será usado para a visualização. Neste caso, todos os objetos do modelo Paciente são recuperados.
    serializer_class = PacienteSerializer # Define a classe de serializer que será usada para serializar e desserializar os objetos Paciente. O serializer é responsável por converter os objetos em dados JSON (ou outros formatos) e vice-versa.