# Generated by Django 3.2.8 on 2021-11-21 07:39

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0004_alter_videocloudinary_video_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videocloudinary',
            name='video_file',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='video'),
        ),
    ]
