# Generated by Django 4.2.4 on 2024-12-03 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Negocio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('logo', models.ImageField(default='logos/default_logo.png', upload_to='logos/')),
                ('direccion_principal', models.CharField(max_length=150)),
                ('direccion_secundaria', models.CharField(blank=True, max_length=150, null=True)),
                ('telefono', models.CharField(max_length=20)),
                ('correo', models.EmailField(max_length=254)),
                ('pagina_web', models.URLField(blank=True, null=True)),
                ('redes_sociales', models.JSONField(blank=True, null=True)),
            ],
        ),
    ]