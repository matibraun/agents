from django.db import migrations


PERSONS_DATA = [
    {
        "first_name": "John",
        "last_name": "Smith",
        "phone_number": "15550101",
        "email": "john.smith@email.com",
        "document_number": "12345678"
    },
    {
        "first_name": "Maria",
        "last_name": "Garcia",
        "phone_number": "15550102",
        "email": "maria.garcia@email.com",
        "document_number": "23456789"
    },
    {
        "first_name": "James",
        "last_name": "Wilson",
        "phone_number": "15550103",
        "email": "james.wilson@email.com",
        "document_number": "34567890"
    },
    {
        "first_name": "Sarah",
        "last_name": "Johnson",
        "phone_number": "15550104",
        "email": "sarah.johnson@email.com",
        "document_number": "45678901"
    },
    {
        "first_name": "Michael",
        "last_name": "Brown",
        "phone_number": "15550105",
        "email": "michael.brown@email.com",
        "document_number": "56789012"
    },
    {
        "first_name": "Emma",
        "last_name": "Davis",
        "phone_number": "15550106",
        "email": "emma.davis@email.com",
        "document_number": "67890123"
    },
    {
        "first_name": "William",
        "last_name": "Martinez",
        "phone_number": "15550107",
        "email": "william.martinez@email.com",
        "document_number": "78901234"
    },
    {
        "first_name": "Sofia",
        "last_name": "Anderson",
        "phone_number": "15550108",
        "email": "sofia.anderson@email.com",
        "document_number": "89012345"
    },
    {
        "first_name": "David",
        "last_name": "Taylor",
        "phone_number": "15550109",
        "email": "david.taylor@email.com",
        "document_number": "90123456"
    },
    {
        "first_name": "Isabella",
        "last_name": "Thomas",
        "phone_number": "15550110",
        "email": "isabella.thomas@email.com",
        "document_number": "01234567"
    },
    {
        "first_name": "Joseph",
        "last_name": "Moore",
        "phone_number": "15550111",
        "email": "joseph.moore@email.com",
        "document_number": "12345678"
    },
    {
        "first_name": "Olivia",
        "last_name": "Jackson",
        "phone_number": "15550112",
        "email": "olivia.jackson@email.com",
        "document_number": "23456789"
    },
    {
        "first_name": "Ethan",
        "last_name": "White",
        "phone_number": "15550113",
        "email": "ethan.white@email.com",
        "document_number": "34567890"
    },
    {
        "first_name": "Ava",
        "last_name": "Harris",
        "phone_number": "15550114",
        "email": "ava.harris@email.com",
        "document_number": "45678901"
    },
    {
        "first_name": "Alexander",
        "last_name": "Martin",
        "phone_number": "15550115",
        "email": "alexander.martin@email.com",
        "document_number": "56789012"
    },
    {
        "first_name": "Matias",
        "last_name": "Braun",
        "phone_number": "+5491155786551",
        "email": "matibraun@gmail.com",
        "document_number": "67890123"
    },
    {
        "first_name": "Daniel",
        "last_name": "Lee",
        "phone_number": "15550117",
        "email": "daniel.lee@email.com",
        "document_number": "78901234"
    },
    {
        "first_name": "Charlotte",
        "last_name": "Clark",
        "phone_number": "15550118",
        "email": "charlotte.clark@email.com",
        "document_number": "89012345"
    },
    {
        "first_name": "Matthew",
        "last_name": "Rodriguez",
        "phone_number": "15550119",
        "email": "matthew.rodriguez@email.com",
        "document_number": "90123456"
    },
    {
        "first_name": "Amelia",
        "last_name": "Lewis",
        "phone_number": "15550120",
        "email": "amelia.lewis@email.com",
        "document_number": "01234567"
    }
]

def preload_persons(apps, schema_editor):
    Person = apps.get_model('agent_1', 'Person')
    persons_to_create = []
    
    for person_data in PERSONS_DATA:
        person = Person(
            first_name=person_data['first_name'],
            last_name=person_data['last_name'],
            phone_number=person_data['phone_number'],
            email=person_data['email'],
            document_number=person_data['document_number']
        )
        persons_to_create.append(person)
    
    Person.objects.bulk_create(persons_to_create)

class Migration(migrations.Migration):

    dependencies = [
        ('agent_1', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(preload_persons),
    ]
