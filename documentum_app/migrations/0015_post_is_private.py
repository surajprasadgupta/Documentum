# Generated by Django 2.1.7 on 2019-10-04 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentum_app', '0014_post_file_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_private',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
