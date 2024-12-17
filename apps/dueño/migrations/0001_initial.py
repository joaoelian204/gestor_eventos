from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('servicios', '0002_delete_tiposervicio_servicio_imagen_referencial_and_more'),  # Asegúrate de que esta dependencia es correcta
    ]

    operations = [
        migrations.CreateModel(
            name='Combo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField()),
                ('precio', models.DecimalField(max_digits=10, decimal_places=2)),
                ('servicios_incluidos', models.ManyToManyField(blank=True, related_name='combos', to='servicios.servicio')),
            ],
        ),
    ]
