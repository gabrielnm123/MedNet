from django.db import models

# Create your models here.

class Paciente(models.Model):
    prontuario = models.IntegerField(primary_key=True, verbose_name='Prontuário')
    nome = models.CharField(
        max_length=100, # 100 pixeos para o campo
        verbose_name='Paciente' # como ele é expressado
    )
    clinica = models.CharField(max_length=100, verbose_name='Clínica')
    leito = models.CharField(max_length=100, verbose_name='Leito')
    comunicado_interno = models.TextField(blank=True, null=True, verbose_name='C.I')
    internado = models.BooleanField(default=True)
    data_registro = models.DateTimeField(
        auto_now_add=True, # auto_now=True, sempre coloca a hora atual
        verbose_name='Data de Registro'
    )

    class Meta: # pra mudar o nome da tabale pra paciente, se não ia ser core_paciente -- cuidado caso faça migrate tem que desfazer, por conta do nome dele que muda
        db_table = 'paciente'

    def save(self, *args, **kwargs):
        # Transforma o nome do paciente em letras maiúsculas antes de salvar
        self.nome = self.nome.upper().strip()
        self.clinica = self.clinica.upper().strip()
        self.leito = self.leito.upper().strip()
        if self.comunicado_interno == None:
            self.comunicado_interno = ''
        elif self.comunicado_interno.strip() == '':
            self.comunicado_interno = ''
        else:
            self.comunicado_interno = self.comunicado_interno.upper().strip()
        super(Paciente, self).save(*args, **kwargs)    
    
    def __str__(self) -> str: # aparece o nome do paciente em vez de Internacao object(1)
        return self.nome
