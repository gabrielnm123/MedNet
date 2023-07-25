from django.db import models
from django.contrib.auth.models import User
from smart_selects.db_fields import ChainedForeignKey # smart_selects para criar campos de seleção encadeados que dependem uns dos outros

# Create your models here.

class Bloco(models.Model):
    bloco = models.CharField(max_length=100)

    class Meta:
        db_table = 'bloco'

    def __str__(self):
        return self.bloco

class Enfermaria(models.Model):
    bloco = models.ForeignKey(Bloco, on_delete=models.CASCADE)
    enfermaria = models.CharField(max_length=100) # Este é um campo para armazenar valores inteiros.

    class Meta:
        db_table = 'enfermaria'

    def __str__(self):
        return self.enfermaria

class Leito(models.Model):
    enfermaria = models.ForeignKey(Enfermaria, on_delete=models.CASCADE)
    leito = models.CharField(max_length=100)

    class Meta:
        db_table = 'leito'

    def __str__(self):
        return self.leito

class Parentesco(models.Model):
    parentesco = models.CharField(max_length=100, verbose_name='Parentesco')

    class Meta:
        db_table = 'parentesco'
    
    def __str__(self) -> str:
        return self.parentesco

class Paciente(models.Model):
    paciente = models.CharField(
        max_length=100, # 100 pixeos para o campo
        verbose_name='Paciente' # como ele é expressado
    )
    bloco = models.ForeignKey(Bloco, on_delete=models.CASCADE)
    enfermaria = ChainedForeignKey(
        Enfermaria,
        chained_field="bloco", # chained_field: Este é o nome do campo no modelo atual que este campo depende. Aqui o campo enfermaria depende do campo bloco, então o valor de chained_field é "bloco". O campo leito depende do campo enfermaria, então o valor de chained_field é "enfermaria".
        chained_model_field="bloco", # chained_model_field: Este é o nome do campo no modelo relacionado que corresponde ao campo especificado em chained_field. Aqui o modelo relacionado para o campo enfermaria é Enfermaria, e o campo correspondente no modelo Enfermaria é bloco, então o valor de chained_model_field é "bloco". O modelo relacionado para o campo leito é Leito, e o campo correspondente no modelo Leito é enfermaria, então o valor de chained_model_field é "enfermaria".
        show_all=False, # show_all: Se este parâmetro for definido como True, todas as opções disponíveis serão mostradas no campo de seleção, independentemente da seleção do usuário no campo especificado em chained_field. Se for definido como False, apenas as opções relevantes serão mostradas com base na seleção do usuário.
        auto_choose=True, # auto_choose: Se este parâmetro for definido como True e houver apenas uma opção disponível, essa opção será selecionada automaticamente.
        sort=True #  Quando sort=True, as opções serão apresentadas em ordem alfabética, facilitando a visualização e seleção para o usuário. Se sort=False, as opções serão exibidas na ordem em que foram cadastradas no banco de dados, sem qualquer ordenação específica.
        )
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
        unique_together = ['bloco', 'enfermaria', 'leito']

    def save(self, *args, **kwargs):
        # Transforma o nome do paciente em letras maiúsculas antes de salvar
        self.paciente = self.paciente.upper()
        super(Paciente, self).save(*args, **kwargs)    
    
    def __str__(self) -> str: # aparece o nome do paciente em vez de Internacao object(1)
        return self.paciente

class Acompanhante(models.Model):
    data_registro_acompanhante = models.DateTimeField(
        auto_now=True, verbose_name='Data de Registro do Acompanhante')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name='Paciente')
    acompanhante = models.CharField(max_length=100, verbose_name='Acompanhante')
    parentesco = models.ForeignKey(Parentesco, on_delete=models.CASCADE, verbose_name='Parentesco')
    contato1 = models.CharField(max_length=11, blank=True, null=True, verbose_name='Contado (1)')
    contato2 = models.CharField(max_length=11, blank=True, null=True, verbose_name='Contado (2)')
    observacao = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')

    class Meta:
        db_table = 'acompanhante'

    def save(self, *args, **kwargs):
        self.acompanhante = self.acompanhante.upper()
        super(Acompanhante, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.acompanhante

class Visitante(models.Model):
    data_registro_visitante = models.DateTimeField(
        auto_now=True, verbose_name='Data de Registro do Visitante')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name='Paciente')
    visitante = models.CharField(max_length=100, verbose_name='Visitante')    
    parentesco = models.ForeignKey(Parentesco, on_delete=models.CASCADE, verbose_name='Parentesco')
    contato1 = models.CharField(max_length=11, blank=True, null=True, verbose_name='Contado (1)')
    contato2 = models.CharField(max_length=11, blank=True, null=True, verbose_name='Contado (2)')
    observacao = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')

    class Meta:
        db_table = 'visitante'

    def save(self, *args, **kwargs):
        self.visitante = self.visitante.upper()
        super(Visitante, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.visitante
