# Generated by Django 3.2.4 on 2021-06-21 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='uploads/products/%Y/%m/%d/'),
        ),
    ]
