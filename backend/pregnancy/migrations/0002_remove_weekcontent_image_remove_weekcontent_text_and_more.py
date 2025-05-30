# Generated by Django 5.2 on 2025-04-12 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pregnancy', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='weekcontent',
            name='image',
        ),
        migrations.RemoveField(
            model_name='weekcontent',
            name='text',
        ),
        migrations.RemoveField(
            model_name='weekcontent',
            name='title',
        ),
        migrations.AddField(
            model_name='weekcontent',
            name='baby_development_image',
            field=models.ImageField(blank=True, null=True, upload_to='baby_development_images/'),
        ),
        migrations.AddField(
            model_name='weekcontent',
            name='baby_development_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='weekcontent',
            name='highlights_this_week_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='weekcontent',
            name='pregnancy_symptoms_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
