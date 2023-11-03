# Generated by Django 4.2.3 on 2023-11-03 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('prontuario', models.IntegerField(primary_key=True, serialize=False, verbose_name='Prontuário')),
                ('nome', models.CharField(max_length=100, verbose_name='Paciente')),
                ('clinica', models.CharField(max_length=100, verbose_name='Clínica')),
                ('leito', models.CharField(max_length=100, verbose_name='Leito')),
                ('comunicado_interno', models.TextField(blank=True, null=True, verbose_name='C.I')),
                ('internado', models.BooleanField(default=True)),
                ('data_registro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Registro')),
            ],
            options={
                'db_table': 'paciente',
            },
        ),
    ]
