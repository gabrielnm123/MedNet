from django.contrib import admin
from django.http import HttpResponse
from core.models import *
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from dal import autocomplete
from django import forms
import pandas as pd
from django.utils.timezone import make_naive

# Register your models here.

def exportar_acompanhantes_para_excel(modeladmin, request, queryset):
    data = {
        'PACIENTE': [],
        'ACOMPANHANTE': [],
        'BLOCO': [],
        'ENFERMARIA': [],
        'LEITO': [],
        'DATA DE REGISTRO DO ACOMPANHANTE': [],
        'USUÁRIO': [],
    }

    for acompanhante in queryset:
        data['PACIENTE'].append(acompanhante.paciente.paciente)
        data['ACOMPANHANTE'].append(acompanhante.acompanhante)
        data['BLOCO'].append(acompanhante.paciente.bloco.bloco)
        data['ENFERMARIA'].append(acompanhante.paciente.enfermaria.enfermaria)
        data['LEITO'].append(acompanhante.paciente.leito.leito)
        data['DATA DE REGISTRO DO ACOMPANHANTE'].append(make_naive(acompanhante.data_registro_acompanhante))
        data['USUÁRIO'].append(acompanhante.usuario.username)

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=acompanhantes.xlsx'
    df.to_excel(response, index=False)
    return response

exportar_acompanhantes_para_excel.short_description = "Exportar para Excel"

def exportar_visitantes_para_excel(modeladmin, request, queryset):
    data = {
        'PACIENTE': [],
        'VISITANTE': [],
        'BLOCO': [],
        'ENFERMARIA': [],
        'LEITO': [],
        'DATA DE REGISTRO DO VISITANTE': [],
        'USUÁRIO': [],
    }

    for visitante in queryset:
        data['PACIENTE'].append(visitante.paciente.paciente)
        data['VISITANTE'].append(visitante.visitante)
        data['BLOCO'].append(visitante.paciente.bloco.bloco)
        data['ENFERMARIA'].append(visitante.paciente.enfermaria.enfermaria)
        data['LEITO'].append(visitante.paciente.leito.leito)
        data['DATA DE REGISTRO DO VISITANTE'].append(make_naive(visitante.data_registro_visitante))
        data['USUÁRIO'].append(visitante.usuario.username)

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=visitantes.xlsx'
    df.to_excel(response, index=False)
    return response

exportar_visitantes_para_excel.short_description = "Exportar para Excel"

class PacienteAdmin(admin.ModelAdmin):
    search_fields = ['paciente']
    list_display = ('paciente', 'data_registro_paciente', 'bloco', 'enfermaria', 'leito','usuario') # pra aparecer no resgistro do paciente logo de cara
    list_filter = ('paciente', 'data_registro_paciente', 'bloco', 'usuario') # pra filtrar

class BlocoFilter(SimpleListFilter):
    title = _('Bloco')
    parameter_name = 'bloco'

    def lookups(self, request, model_admin):
        blocos = Bloco.objects.all()
        return [(bloco.bloco, bloco.bloco) for bloco in blocos]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(paciente__bloco__bloco=self.value())

class AcompanhanteAdminForm(forms.ModelForm):
    class Meta:
        model = Acompanhante
        fields = '__all__'
        widgets = {
            'paciente': autocomplete.ModelSelect2(url='paciente-autocomplete')
        }

class VisitanteAdminForm(forms.ModelForm):
    class Meta:
        model = Visitante
        fields = '__all__'
        widgets = {
            'paciente': autocomplete.ModelSelect2(url='paciente-autocomplete')
        }

class AcompanhanteAdmin(admin.ModelAdmin):
    form = AcompanhanteAdminForm
    search_fields = ['paciente__paciente', 'acompanhante']
    list_display = ('paciente', 'acompanhante', 'parentesco', 'get_bloco', 'get_enfermaria', 'get_leito', 'data_registro_acompanhante', 'documento', 'usuario')
    list_filter = ('data_registro_acompanhante', BlocoFilter, 'usuario') # usuario não esta sendo filtrado

    def get_bloco(self, obj):
        return obj.paciente.bloco.bloco

    def get_enfermaria(self, obj):
        return obj.paciente.enfermaria.enfermaria

    def get_leito(self, obj):
        return obj.paciente.leito.leito

    get_bloco.admin_order_field = 'paciente__bloco__bloco'
    get_bloco.short_description = 'Bloco'

    get_enfermaria.admin_order_field = 'paciente__enfermaria__enfermaria'
    get_enfermaria.short_description = 'Enfermaria'

    get_leito.admin_order_field = 'paciente__leito__leito'
    get_leito.short_description = 'Leito'

    actions = [exportar_acompanhantes_para_excel]
    
class VisitanteAdmin(admin.ModelAdmin):
    form = VisitanteAdminForm
    search_fields = ['paciente__paciente', 'vizitante']
    list_display = ('paciente', 'visitante', 'parentesco', 'get_bloco', 'get_enfermaria', 'get_leito', 'data_registro_visitante', 'documento', 'usuario')
    list_filter = ('data_registro_visitante', BlocoFilter, 'usuario') # usuario não esta sendo filtrado

    def get_bloco(self, obj):
        return obj.paciente.bloco.bloco

    def get_enfermaria(self, obj):
        return obj.paciente.enfermaria.enfermaria

    def get_leito(self, obj):
        return obj.paciente.leito.leito

    get_bloco.admin_order_field = 'paciente__bloco__bloco'
    get_bloco.short_description = 'Bloco'

    get_enfermaria.admin_order_field = 'paciente__enfermaria__enfermaria'
    get_enfermaria.short_description = 'Enfermaria'

    get_leito.admin_order_field = 'paciente__leito__leito'
    get_leito.short_description = 'Leito'
    
    actions = [exportar_visitantes_para_excel]

admin.site.register(Paciente, PacienteAdmin)
admin.site.register(Acompanhante, AcompanhanteAdmin)
admin.site.register(Visitante, VisitanteAdmin)
