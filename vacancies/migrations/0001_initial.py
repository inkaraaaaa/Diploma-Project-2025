# Generated by Django 4.2.19 on 2025-04-16 18:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sendreview', '0002_remove_comment_company_remove_comment_student_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('job_type', models.CharField(max_length=50)),
                ('experience_required', models.CharField(max_length=50)),
                ('level', models.CharField(max_length=50)),
                ('location', models.CharField(max_length=255)),
                ('course', models.CharField(default='None', max_length=100)),
                ('about_role', models.TextField(blank=True, null=True)),
                ('responsibilities', models.TextField(blank=True, null=True)),
                ('requirements', models.TextField(blank=True, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sendreview.company')),
            ],
        ),
    ]
