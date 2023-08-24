from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Parentesco(models.Model):
    parentesco = models.CharField(max_length=100, verbose_name='Parentesco')

    class Meta:
        db_table = 'parentesco'
    
    def save(self, *args, **kwargs):
        self.parentesco = self.parentesco.upper().strip()
        super(Parentesco, self).save(*args, *kwargs)
    
    def __str__(self) -> str:
        return self.parentesco

class Paciente(models.Model):
    prontuario = models.IntegerField(primary_key=True, verbose_name='Prontuário')
    nome = models.CharField(
        max_length=100, # 100 pixeos para o campo
        verbose_name='Paciente' # como ele é expressado
    )
    clinica = models.CharField(max_length=100, verbose_name='Clínica')
    leito = models.CharField(max_length=100, verbose_name='Leito')
    comunicado_interno = models.TextField(blank=True, null=True, verbose_name='C.I')
    data_registro_paciente = models.DateTimeField(
        auto_now=True, # auto_now=True, sempre coloca a hora atual
        verbose_name='Data de Registro do Paciente'
    )

    class Meta: # pra mudar o nome da tabale pra paciente, se não ia ser core_paciente -- cuidado caso faça migrate tem que desfazer, por conta do nome dele que muda
        db_table = 'paciente'

    def save(self, *args, **kwargs):
        # Transforma o nome do paciente em letras maiúsculas antes de salvar
        self.nome = self.nome.upper().strip()
        self.clinica = self.clinica.upper().strip()
        self.leito = self.leito.upper().strip()
        if self.comunicado_interno != None:
            self.comunicado_interno = self.comunicado_interno.upper().strip()
        super(Paciente, self).save(*args, **kwargs)    
    
    def __str__(self) -> str: # aparece o nome do paciente em vez de Internacao object(1)
        return self.nome

class Visitante(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name='Paciente')
    nome = models.CharField(max_length=100, verbose_name='Visitante')    
    parentesco = models.ForeignKey(Parentesco, on_delete=models.CASCADE, verbose_name='Parentesco')
    documento = models.CharField(max_length=100, blank=True, null=True, verbose_name='Documento')
    data_registro_visitante = models.DateTimeField(
        auto_now=True, verbose_name='Data de Registro do Visitante')
    operador = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Operador')

    class Meta:
        db_table = 'visitante'

    def save(self, *args, **kwargs):
        self.nome = self.nome.upper().strip()
        if self.documento != None:
            self.documento = self.documento.upper().strip()
        super(Visitante, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.nome
