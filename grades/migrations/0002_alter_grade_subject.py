# Generated by Django 5.1.4 on 2025-01-19 17:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_submission_subject'),
        ('grades', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='account.subject'),
        ),
    ]
