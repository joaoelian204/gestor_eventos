# Generated by Django 5.1.3 on 2024-12-11 00:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_imagenpublicacion_descripcion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='megusta',
            name='publicacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='me_gustas', to='blog.publicacion'),
        ),
    ]
