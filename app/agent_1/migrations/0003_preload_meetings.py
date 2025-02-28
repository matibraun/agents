from django.db import migrations
from django.utils import timezone
import random
from datetime import timedelta

def preload_meetings(apps, schema_editor):
    Meeting = apps.get_model('agent_1', 'Meeting')
    meetings_to_create = []
    
    base_datetime = timezone.now()
    
    for _ in range(50):

        person_id = random.randint(1, 20)
        
        random_days = random.randint(0, 9)
        random_hour = random.randint(8, 17)
        random_minute = random.choice([0, 15, 30, 45])
        
        meeting_datetime = base_datetime + timedelta(days=random_days)
        meeting_datetime = meeting_datetime.replace(
            hour=random_hour,
            minute=random_minute,
            second=0,
            microsecond=0
        )
        
        meeting = Meeting(
            person_id=person_id,
            datetime=meeting_datetime
        )
        meetings_to_create.append(meeting)
    
    Meeting.objects.bulk_create(meetings_to_create)


class Migration(migrations.Migration):
    dependencies = [
        ('agent_1', '0002_preload_persons'),
    ]

    operations = [
        migrations.RunPython(preload_meetings),
    ]