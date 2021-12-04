# Generated by Django 3.2.8 on 2021-12-04 01:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('unhindled', '0011_alter_post_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='inbox',
            name='comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='unhindled.comment'),
        ),
        migrations.AddField(
            model_name='inbox',
            name='like',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='unhindled.like'),
        ),
        migrations.AddField(
            model_name='inbox',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='unhindled.post'),
        ),
    ]
