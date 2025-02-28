from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    document_number = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = "People"

class Meeting(models.Model):

    STATUS_CHOICES = [
        ('scheduled', 'scheduled'),
        ('confirmed', 'Confirmed'),
        ('rescheduled', 'Rescheduled'),
        ('canceled', 'Canceled'),
    ]

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='meetings')
    datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Meeting with {self.person} on {self.datetime}"

class Conversation(models.Model):
    MESSAGE_TYPES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='conversations')
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.message_type.title()} message from {self.person}"