from django.db import models
from django.contrib.auth.models import User
from smart_selects.db_fields import ChainedForeignKey

# Create your models here.

class Bloco(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        db_table = 'bloco'

    def __str__(self):
        return self.nome

class Enfermaria(models.Model):
    bloco = models.ForeignKey(Bloco, on_delete=models.CASCADE)
    numero = models.IntegerField() # Este é um campo para armazenar valores inteiros.

    class Meta:
        db_table = 'enfermaria'

    def __str__(self):
        return f"Enfermaria {self.numero} - Bloco {self.bloco}"

class Leito(models.Model):
    enfermaria = models.ForeignKey(Enfermaria, on_delete=models.CASCADE)
    numero = models.IntegerField()

    class Meta:
        db_table = 'leito'

    def __str__(self):
        return f"Leito {self.numero} - Enfermaria {self.enfermaria}"

class Paciente(models.Model):
    paciente = models.CharField(
        max_length=100, # 100 pixeos para o campo
        verbose_name='Paciente' # como ele é expressado
    )
    # Observacao = models.TextField(
    #     blank=True, # pode ser branco
    #     null=True # pode ser nulo
    # )
    bloco = models.ForeignKey(Bloco, on_delete=models.CASCADE)
    enfermaria = ChainedForeignKey(
        Enfermaria,
        chained_field="bloco", # chained_field: Este é o nome do campo no modelo atual que este campo depende. Aqui o campo enfermaria depende do campo bloco, então o valor de chained_field é "bloco". O campo leito depende do campo enfermaria, então o valor de chained_field é "enfermaria".
        chained_model_field="bloco", # chained_model_field: Este é o nome do campo no modelo relacionado que corresponde ao campo especificado em chained_field. Aqui o modelo relacionado para o campo enfermaria é Enfermaria, e o campo correspondente no modelo Enfermaria é bloco, então o valor de chained_model_field é "bloco". O modelo relacionado para o campo leito é Leito, e o campo correspondente no modelo Leito é enfermaria, então o valor de chained_model_field é "enfermaria".
        show_all=False, # show_all: Se este parâmetro for definido como True, todas as opções disponíveis serão mostradas no campo de seleção, independentemente da seleção do usuário no campo especificado em chained_field. Se for definido como False, apenas as opções relevantes serão mostradas com base na seleção do usuário.
        auto_choose=True, # auto_choose: Se este parâmetro for definido como True e houver apenas uma opção disponível, essa opção será selecionada automaticamente.
        sort=True)
    leito = ChainedForeignKey(
        Leito,
        chained_field="enfermaria",
        chained_model_field="enfermaria",
        show_all=False,
        auto_choose=True,
        sort=True)
    usuario = models.ForeignKey( # para poder vincular a um usuario
        User,
        on_delete=models.CASCADE, # se apagar usuário todos os pacientes criados por esse usuario é apagado em cascata
        verbose_name='Usuário'
    )
    data_registro_paciente = models.DateTimeField(
        auto_now=True, # auto_now=True, sempre coloca a hora atual
        verbose_name='Data de Registro do Paciente'
    )

    class Meta: # pra mudar o nome da tabale pra paciente, se não ia ser core_paciente -- cuidado caso faça migrate tem que desfazer, por conta do nome dele que muda
        db_table = 'paciente'

    def __str__(self) -> str: # aparece o nome do paciente em vez de Internacao object(1)
        return self.paciente

class Acompanhante(models.Model):
    acompanhante = models.CharField(max_length=100, verbose_name='Acompanhante')
    data_registro_acompanhante = models.DateTimeField(
        auto_now=True, verbose_name='Data de Registro do Acompanhante')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name='Paciente')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')

    class Meta:
        db_table = 'acompanhante'

    def __str__(self) -> str:
        return self.acompanhante
