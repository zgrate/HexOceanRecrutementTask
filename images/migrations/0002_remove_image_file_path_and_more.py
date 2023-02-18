# Generated by Django 4.1.6 on 2023-02-16 14:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='file_path',
        ),
        migrations.RemoveField(
            model_name='image',
            name='original_file_name',
        ),
        migrations.AddField(
            model_name='image',
            name='image_owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='image',
            name='original_image',
            field=models.ImageField(default='default.jpg', upload_to=''),
        ),
    ]
