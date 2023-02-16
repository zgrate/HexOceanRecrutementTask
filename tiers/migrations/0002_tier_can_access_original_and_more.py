# Generated by Django 4.1.6 on 2023-02-16 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tier',
            name='can_access_original',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tier',
            name='can_generate_expire_links',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tier',
            name='tier_name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
