# Generated by Django 3.2.8 on 2021-11-26 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unhindled', '0008_merge_20211126_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followrequest',
            name='author',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='followrequest',
            name='follower',
            field=models.CharField(max_length=200),
        ),
    ]