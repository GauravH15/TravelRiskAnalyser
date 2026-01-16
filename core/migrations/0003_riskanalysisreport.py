# Generated migration for RiskAnalysisReport model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_trip'),
    ]

    operations = [
        migrations.CreateModel(
            name='RiskAnalysisReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('overall_risk_score', models.IntegerField(default=0)),
                ('risk_level', models.CharField(choices=[('Low', 'Low Risk'), ('Medium', 'Medium Risk'), ('High', 'High Risk')], max_length=20)),
                ('weather_risk_score', models.IntegerField(default=0)),
                ('disease_risk_score', models.IntegerField(default=0)),
                ('full_report', models.JSONField(default=dict)),
                ('top_risks', models.JSONField(default=list)),
                ('recommendations', models.JSONField(default=list)),
                ('executive_summary', models.TextField(blank=True)),
                ('weather_report', models.JSONField(default=dict)),
                ('disease_report', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('trip', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='risk_analysis', to='core.trip')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
