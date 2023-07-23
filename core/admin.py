from django.contrib import admin
from core.models import Bloco, Enfermaria, Leito, Paciente, Acompanhante
# Register your models here.

class PacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'data_registro_paciente', 'usuario') # pra aparecer no resgistro do paciente logo de cara
    list_filter = ('paciente', 'data_registro_paciente', 'usuario') # pra filtrar

class AcompanhanteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'acompanhante', 'data_registro_acompanhante', 'usuario')
    list_filter = ('paciente', 'acompanhante', 'data_registro_acompanhante', 'usuario')

admin.site.register(Bloco)
admin.site.register(Enfermaria)
admin.site.register(Leito)
admin.site.register(Paciente, PacienteAdmin)
admin.site.register(Acompanhante, AcompanhanteAdmin)
