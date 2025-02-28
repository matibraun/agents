from django.views.decorators.csrf import csrf_exempt
import json
import csv
import os
from datetime import datetime, timedelta
from django.http import JsonResponse
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_community.llms import Cohere
from langchain.tools import BaseTool
from twilio.rest import Client


# Tool for sending WhatsApp messages via Twilio
import json

class WhatsAppTool(BaseTool):
    name: str = "WhatsApp Tool"
    description: str = "Tool for sending WhatsApp messages via Twilio."

    def _run(self, input_text: str):
        try:
            # Ensure the input is in correct JSON format (expects a string)
            if isinstance(input_text, str):
                input_text = input_text.strip()  # Strip any leading/trailing whitespaces
                input_text = input_text.replace("'", '"')  # Replace single quotes with double quotes if necessary

                # Convert the corrected string to a dictionary
                input_text = json.loads(input_text)

            # Extract the phone number and message
            phone_number = input_text.get("phone_number")
            message = input_text.get("message")

            # Check if the phone number is valid and add the "whatsapp:" prefix if missing
            if phone_number and not phone_number.startswith("whatsapp:"):
                phone_number = f"whatsapp:{phone_number}"

            # If phone_number is still None or invalid, handle it gracefully
            if not phone_number:
                raise ValueError("Invalid phone number format.")

            # Twilio credentials from environment variables (for security)
            TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
            TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
            TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

            # Initialize Twilio Client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

            # Send the WhatsApp message
            msg = client.messages.create(
                body=message,
                from_=TWILIO_WHATSAPP_NUMBER,
                to=phone_number
            )

            print(f"WhatsApp message sent to {phone_number}: {msg.sid}")
            return "Message sent."

        except json.JSONDecodeError as e:
            print(f"JSON error: {str(e)}")
            return f"Failed to decode the input: {str(e)}"
        
        except ValueError as e:
            print(f"Value error: {str(e)}")
            return f"Failed to send message: {str(e)}"
        
        except Exception as e:
            print(f"Error sending WhatsApp message: {str(e)}")
            return f"Failed to send message: {str(e)}"


# Tool for updating the CSV with meeting confirmation
class CSVUpdateTool(BaseTool):
    name: str = "CSV Update Tool"
    description: str = "Tool to update meeting confirmations in a CSV file."

    def _run(self, meeting_id: str, confirmed: bool, comments: str):
        updated = False
        new_rows = []
        csv_path = os.path.join(os.path.dirname(__file__), "data", "meetings.csv")

        with open(csv_path, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for row in reader:
                if row["meeting_id"] == str(meeting_id):
                    row["confirmed"] = "true" if confirmed else "false"
                    row["comments"] = comments
                    updated = True
                new_rows.append(row)

        if updated:
            with open(csv_path, mode="w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(new_rows)
            return "CSV updated successfully."
        else:
            return f"Meeting ID {meeting_id} not found."


# Initialize LangChain with Cohere
llm = Cohere(temperature=0.7)
whatsapp_tool = WhatsAppTool()
csv_update_tool = CSVUpdateTool()

# Define tools as a list
tools = [
    Tool(name="SendWhatsApp", func=whatsapp_tool.run, description="Send WhatsApp messages."),
    Tool(name="UpdateCSV", func=csv_update_tool.run, description="Update meeting confirmations in CSV."),
]

# Initialize the agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose=True,
)







# Django view to trigger sending WhatsApp messages and updating CSV for meetings scheduled for tomorrow
def start_agent(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method is allowed."}, status=405)

    tomorrow = (datetime.now() + timedelta(days=1)).date()

    # Read the CSV for meetings scheduled for tomorrow
    csv_path = os.path.join(os.path.dirname(__file__), "data", "meetings.csv")
    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        meetings = [row for row in reader if datetime.strptime(row["meeting_date"], "%Y-%m-%d").date() == tomorrow]

    if not meetings:
        return JsonResponse({"message": "No meetings found for tomorrow."})

    # Process each meeting
    for meeting in meetings:
        meeting_id = meeting["meeting_id"]
        name = meeting["name"]
        phone_number = meeting["phone_number"]
        meeting_time = meeting["meeting_time"]

        # Compose the message
        message = f"Hi {name}, please confirm your meeting scheduled for tomorrow at {meeting_time}."

        # Trigger the agent with the WhatsApp tool
        try:
            # Create a JSON string to send to the agent
            input_text = json.dumps(
                {
                    "phone_number": phone_number,
                    "message": message
                }
            )

            # Assuming agent.invoke() can handle a JSON string input
            agent.invoke(input_text)

            # Optionally update CSV after confirmation or based on user interaction
            # (in this example, we'll assume confirmation logic is handled later)
            comments = "User confirmed meeting"  # You can change this logic

            # Assuming a proper format to confirm the meeting
            confirmation_data = json.dumps(
                {
                    "meeting_id": meeting_id,
                    "confirmed": True,
                    "comments": comments
                }
            )
            
            # Second invoke to update the meeting status
            agent.invoke(confirmation_data)

        except Exception as e:
            return JsonResponse({"error": f"Error processing meeting {meeting_id}: {str(e)}"}, status=500)

    return JsonResponse({"message": "All meetings processed."})


import re
from datetime import datetime, timezone
@csrf_exempt
def handle_response(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    try:
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST

        from_number = data.get("From", "").replace("whatsapp:", "").strip()
        message_body = data.get("Body", "").strip()

        if not from_number or not message_body:
            return JsonResponse({"error": "Missing required fields (From, Body)"}, status=400)

        print(f"Received message from {from_number}: {message_body}")

        # Step 1: Use the agent to find `meeting_id`
        meeting_id_query = json.dumps({"phone_number": from_number})
        meeting_id_response = agent.invoke(meeting_id_query)

        if not meeting_id_response or "meeting_id" not in meeting_id_response:
            return JsonResponse({"error": "Meeting not found for this phone number"}, status=404)

        meeting_id = meeting_id_response["meeting_id"]

        # Step 2: Determine Confirmation Status
        confirm_keywords = ["yes", "confirmed", "sure", "okay", "will attend", "confirm"]
        decline_keywords = ["no", "can't", "won't", "not coming", "decline"]

        confirmation_status = None
        if any(re.search(rf"\b{word}\b", message_body, re.IGNORECASE) for word in confirm_keywords):
            confirmation_status = True
        elif any(re.search(rf"\b{word}\b", message_body, re.IGNORECASE) for word in decline_keywords):
            confirmation_status = False

        if confirmation_status is not None:
            # Step 3: Use agent to update the CSV
            update_payload = json.dumps({
                "meeting_id": meeting_id,
                "confirmed": confirmation_status,
                "comments": message_body
            })
            update_response = agent.invoke(update_payload)

            return JsonResponse({"message": update_response})

        # Step 4: If the response is unclear, send a follow-up message
        follow_up_message = "Hi, we received your response but couldn't determine if you're confirming or declining. Please reply with 'Yes' to confirm or 'No' to decline."
        whatsapp_tool.run(json.dumps({"phone_number": from_number, "message": follow_up_message}))

        return JsonResponse({"message": "Follow-up message sent for clarification."})

    except Exception as e:
        print(f"Unexpected error: {e}")
        return JsonResponse({"error": "Internal Server Error"}, status=500)