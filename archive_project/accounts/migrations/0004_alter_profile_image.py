# Generated by Django 4.2.13 on 2024-08-11 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_profile_designation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default=None, upload_to='accounts/media/images/'),
        ),
    ]
