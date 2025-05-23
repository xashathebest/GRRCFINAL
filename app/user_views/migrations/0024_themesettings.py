# Generated by Django 3.2.25 on 2025-05-08 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_views', '0023_auto_20250509_0122'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThemeSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('theme', models.CharField(choices=[('default', 'Default Brand Theme'), ('valentine', "Valentine's Day"), ('pride', 'Pride Month'), ('custom', 'Custom Theme')], default='default', max_length=20)),
                ('is_active', models.BooleanField(default=False)),
                ('primary_color', models.CharField(default='#A463E6', max_length=7)),
                ('secondary_color', models.CharField(default='#924DD8', max_length=7)),
                ('button_color', models.CharField(default='#A463E6', max_length=7)),
                ('button_hover_color', models.CharField(default='#9F59E6', max_length=7)),
                ('text_color', models.CharField(default='#1F2937', max_length=7)),
                ('background_color', models.CharField(default='#F8FAFC', max_length=7)),
                ('nav_background', models.CharField(default='#A463E6', max_length=7)),
                ('nav_text_color', models.CharField(default='#FFFFFF', max_length=7)),
                ('nav_hover_color', models.CharField(default='#924DD8', max_length=7)),
                ('success_color', models.CharField(default='#10B981', max_length=7)),
                ('warning_color', models.CharField(default='#F59E0B', max_length=7)),
                ('error_color', models.CharField(default='#EF4444', max_length=7)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Theme Setting',
                'verbose_name_plural': 'Theme Settings',
            },
        ),
    ]
