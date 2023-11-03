from django.db import models
from django.contrib.auth.models import User
from core.models import *

# Create your models here.

class Parentesco(models.Model):
    tipo = models.CharField(max_length=100, verbose_name='Parentesco')

    class Meta:
        db_table = 'parentesco'
    
    def save(self, *args, **kwargs):
        self.tipo = self.tipo.upper().strip()
        super(Parentesco, self).save(*args, *kwargs)
    
    def __str__(self) -> str:
        return self.tipo

class Visitante(models.Model):
    data_registro = models.DateTimeField(
        auto_now_add=True, verbose_name='Data de Registro')
    clinica = models.CharField(max_length=100, verbose_name='Clínica')
    leito = models.CharField(max_length=100, verbose_name='Leito')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name='Paciente')
    nome = models.CharField(max_length=100, verbose_name='Visitante')
    parentesco = models.ForeignKey(Parentesco, on_delete=models.CASCADE, verbose_name='Parentesco')
    documento = models.CharField(max_length=100, verbose_name='Documento')
    operador = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Operador')

    class Meta:
        db_table = 'visitante'

    def save(self, *args, **kwargs):
        self.nome = self.nome.upper().strip()
        self.documento = self.documento.upper().strip()
        if self.pk is None:
            self.clinica = self.paciente.clinica
            self.leito = self.paciente.leito
        super(Visitante, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.nome