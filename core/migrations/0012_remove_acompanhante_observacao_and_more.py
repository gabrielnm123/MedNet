# Generated by Django 4.2.3 on 2023-07-27 16:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_visitante_delete_vizitante"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="acompanhante",
            name="observacao",
        ),
        migrations.RemoveField(
            model_name="visitante",
            name="observacao",
        ),
        migrations.AddField(
            model_name="acompanhante",
            name="documento",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="Documento"
            ),
        ),
        migrations.AddField(
            model_name="visitante",
            name="documento",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="Documento"
            ),
        ),
    ]
