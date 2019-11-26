# Generated by Django 2.1.7 on 2019-09-25 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_code', models.IntegerField(blank=True, null=True)),
                ('company_name', models.CharField(blank=True, max_length=255)),
                ('created_date', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
