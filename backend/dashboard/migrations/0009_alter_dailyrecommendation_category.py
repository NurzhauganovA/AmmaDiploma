# Generated by Django 5.2 on 2025-05-03 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_alter_dailyrecommendation_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyrecommendation',
            name='category',
            field=models.CharField(choices=[('vitamins', 'Vitamins'), ('minerals', 'Minerals'), ('macros', 'Macronutrients'), ('hydration', 'Hydration')], default='vitamins', max_length=20),
        ),
    ]
