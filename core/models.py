from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Paciente(models.Model):
    paciente = models.CharField(
        max_length=100, # 100 pixeos para o campo
        verbose_name='Paciente' # como ele é expressado
    )
    # Observacao = models.TextField(
    #     blank=True, # pode ser branco
    #     null=True # pode ser nulo
    # )
    data_registro_paciente = models.DateTimeField(
        auto_now=True, # auto_now=True, sempre coloca a hora atual
        verbose_name='Data de Registro do Paciente'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuário'
    )

    class Meta: # pra mudar o nome da tabale pra paciente, se não ia ser core_paciente -- cuidado caso faça migrate tem que desfazer, por conta do nome dele que muda
        db_table = 'paciente'

    def __str__(self) -> str: # aparece o nome do paciente em vez de Internacao object(1)
        return self.paciente

class Acompanhante(models.Model):
    acompanhante = models.CharField(
        max_length=100,
        verbose_name='Acompanhante'
    )
    data_registro_acompanhante = models.DateTimeField(
        auto_now=True,
        verbose_name='Data de Registro do Acompanhante'
    )
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        verbose_name='Paciente'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuário'
    )

    class Meta:
        db_table = 'acompanhante'

    def __str__(self) -> str:
        return self.acompanhante
