# Generated by Django 5.1.4 on 2025-01-03 04:34

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='description',
            field=ckeditor.fields.RichTextField(default='No description provided'),
            preserve_default=False,
        ),
    ]