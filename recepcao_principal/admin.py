from django.contrib import admin
from django.http import HttpResponse
from .models import *
from dal import autocomplete
from django import forms
import pandas as pd
from django.utils.timezone import make_naive

# Register your models here.

def exportar_visitantes_para_excel(modeladmin, request, queryset):
    data = {
        'DATA DE REGISTRO': [],
        'CLÍNICA': [],
        'LEITO': [],
        'PACIENTE': [],
        'VISITANTE': [],
        'PARENTESCO': [],
        'DOCUMENTO': [],
        'OPERADOR': [],
    }

    for visitante in queryset:
        data['DATA DE REGISTRO'].append(make_naive(visitante.data_registro))
        data['CLÍNICA'].append(visitante.paciente.clinica)
        data['LEITO'].append(visitante.paciente.leito)
        data['PACIENTE'].append(visitante.paciente.nome)
        data['VISITANTE'].append(visitante.nome),
        data['PARENTESCO'].append(visitante.parentesco),
        data['DOCUMENTO'].append(visitante.documento)
        data['OPERADOR'].append(visitante.operador.username)

    df = pd.DataFrame(data)
    df['DATA DE REGISTRO'] = df['DATA DE REGISTRO'].dt.strftime('%d/%m/%Y %H:%M:%S')
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=visitantes.xlsx'
    df.to_excel(response, index=False)
    return response

exportar_visitantes_para_excel.short_description = "Exportar para Excel"

class VisitanteAdminForm(forms.ModelForm):
    class Meta:
        model = Visitante
        fields = '__all__'
        widgets = {
            'paciente': autocomplete.ModelSelect2(url='paciente-autocomplete')
        }

class VisitanteAdmin(admin.ModelAdmin):
    form = VisitanteAdminForm
    search_fields = ['paciente__nome', 'nome', 'paciente__prontuario']
    list_display = ('get_prontuario', 'id', 'paciente', 'nome', 'get_clinica', 'get_leito', 'data_registro', 'parentesco', 'documento', 'operador')
    list_filter = ('data_registro', 'operador', 'paciente__clinica')

    def get_prontuario(self, obj):
        return obj.paciente.prontuario
    
    def get_clinica(self, obj):
        return obj.paciente.clinica

    def get_leito(self, obj):
        return obj.paciente.leito

    get_prontuario.admin_order_field = 'paciente__prontuario'
    get_prontuario.short_description = 'Prontuário'

    get_clinica.admin_order_field = 'paciente__clinica'
    get_clinica.short_description = 'Clínica'

    get_leito.admin_order_field = 'paciente__leito'
    get_leito.short_description = 'Leito'
    
    actions = [exportar_visitantes_para_excel]

admin.site.register(Visitante, VisitanteAdmin)
admin.site.register(Parentesco)
