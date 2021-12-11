# Generated by Django 3.2.8 on 2021-11-21 07:17

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0002_videocloudinary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videocloudinary',
            name='thumbnail',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
    ]
