# Generated by Django 4.2.10 on 2024-08-05 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('electricity', '0002_bill_current_bill_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='current_bill_images',
            field=models.ImageField(blank=True, null=True, upload_to='bills/'),
        ),
    ]
