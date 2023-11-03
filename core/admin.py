from django.contrib import admin
from .models import *

# Register your models here.

class PacienteAdmin(admin.ModelAdmin):
    search_fields = ['nome', 'prontuario']
    list_display = ('prontuario', 'nome', 'clinica', 'leito', 'internado', 'data_registro') # pra aparecer no resgistro do paciente logo de cara
    list_filter = ('internado', 'clinica', 'data_registro')

admin.site.register(Paciente, PacienteAdmin)
