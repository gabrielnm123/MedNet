from django.contrib import admin
from core.models import *
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

# Register your models here.

class PacienteAdmin(admin.ModelAdmin):
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

class AcompanhanteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'acompanhante', 'get_bloco', 'get_enfermaria', 'get_leito', 'data_registro_acompanhante', 'usuario')
    list_filter = ('data_registro_acompanhante', 'paciente', 'acompanhante', BlocoFilter, 'usuario') # usuario não esta sendo filtrado

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

class VizitanteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'vizitante', 'get_bloco', 'get_enfermaria', 'get_leito', 'data_registro_vizitante', 'usuario')
    list_filter = ('data_registro_vizitante', 'paciente', 'vizitante', BlocoFilter, 'usuario') # usuario não esta sendo filtrado

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

admin.site.register(Bloco)
admin.site.register(Enfermaria)
admin.site.register(Leito)
admin.site.register(Paciente, PacienteAdmin)
admin.site.register(Acompanhante, AcompanhanteAdmin)
admin.site.register(Vizitante, VizitanteAdmin)
