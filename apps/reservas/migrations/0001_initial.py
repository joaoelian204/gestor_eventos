# Generated by Django 5.1.3 on 2024-12-03 08:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clientes', '0001_initial'),
        ('eventos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alquiler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_alquiler', models.DateField()),
                ('hora_inicio_reserva', models.TimeField()),
                ('hora_fin_planificada', models.TimeField()),
                ('hora_fin_real', models.TimeField(blank=True, null=True)),
                ('costo_alquiler', models.FloatField()),
                ('calificacion_cliente', models.IntegerField(blank=True, null=True)),
                ('calificacion_negocio', models.IntegerField(blank=True, null=True)),
                ('observacion', models.TextField(blank=True, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clientes.cliente')),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventos.evento')),
            ],
        ),
    ]
