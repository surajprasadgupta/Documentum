# Generated by Django 2.1.7 on 2019-09-23 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentum_app', '0009_auto_20190923_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tags',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
