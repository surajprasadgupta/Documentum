# Generated by Django 2.1.7 on 2019-09-23 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentum_app', '0010_auto_20190923_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tags',
            name='slug',
            field=models.CharField(blank=True, max_length=225, unique=True),
        ),
    ]
