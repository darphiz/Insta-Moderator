# Generated by Django 4.0.4 on 2022-05-17 23:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MAIN', '0007_followerbank'),
    ]

    operations = [
        migrations.CreateModel(
            name='Violator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='violators', to='MAIN.process')),
            ],
        ),
    ]