# Generated by Django 4.2.19 on 2025-05-02 17:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sendreview', '0002_remove_comment_company_remove_comment_student_and_more'),
        ('vacancies', '0003_application'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joblisting',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_listings', to='sendreview.company'),
        ),
    ]
