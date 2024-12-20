# Generated by Django 5.1.3 on 2024-12-10 21:57

import cloudinary.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_remove_publicacion_imagen_imagenpublicacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagenpublicacion',
            name='descripcion',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='publicacion',
            name='imagen_principal',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='publicaciones'),
        ),
        migrations.AlterField(
            model_name='imagenpublicacion',
            name='imagen',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='publicaciones/galeria'),
        ),
        migrations.AlterField(
            model_name='imagenpublicacion',
            name='publicacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='galeria', to='blog.publicacion'),
        ),
    ]
