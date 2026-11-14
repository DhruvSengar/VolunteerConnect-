from django.db import migrations

def seed_milestones(apps, schema_editor):
    Milestone = apps.get_model('core', 'Milestone')
    for hours in (25, 50, 100):
        Milestone.objects.get_or_create(required_hours=hours, defaults={'name': f'{hours}-Hour Milestone', 'description': f'Completed {hours} verified service hours.'})

class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial')]
    operations = [migrations.RunPython(seed_milestones, migrations.RunPython.noop)]
