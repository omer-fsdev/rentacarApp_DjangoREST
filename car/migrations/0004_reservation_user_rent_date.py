# Generated by Django 4.2.1 on 2023-06-13 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car', '0003_reservation'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='reservation',
            constraint=models.UniqueConstraint(fields=('customer', 'start_date', 'end_date'), name='user_rent_date'),
        ),
    ]
