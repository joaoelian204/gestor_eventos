# Generated by Django 5.1.3 on 2024-12-09 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='correo',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
