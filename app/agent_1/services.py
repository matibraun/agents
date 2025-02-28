import os
from django.core.exceptions import ObjectDoesNotExist
from agent_1.models import Conversation, Person
from twilio.rest import Client


class WhatsAppService:

    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"


    @classmethod
    def send_message(cls, phone_number: str, message_content: str) -> str:
        """Sends a WhatsApp message and logs it in the Conversation model."""
        try:


            # Fetch the existing person


            whatsapp_phone_number = f"whatsapp:{phone_number}"

            client = Client(cls.TWILIO_ACCOUNT_SID, cls.TWILIO_AUTH_TOKEN)
            msg = client.messages.create(
                body=message_content,
                from_=cls.TWILIO_WHATSAPP_NUMBER,
                to=whatsapp_phone_number
            )

            # esto sacarlo de este metodo
            try:
                person = Person.objects.get(phone_number=phone_number)
            except ObjectDoesNotExist:
                return f"Person with phone number {phone_number} does not exist."
            
            # Log message in DB
            Conversation.objects.create(
                person=person,
                message=message_content,
                message_type="outgoing"
            )

            print(f"WhatsApp message sent to {phone_number}: {msg.sid}")
            return "Message sent."

        except Exception as e:
            print(f"Error sending WhatsApp message: {str(e)}")
            return f"Failed to send message: {str(e)}"

