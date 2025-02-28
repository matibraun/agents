from django.utils import timezone
from datetime import timedelta
from agent_1.services import WhatsAppService
from rest_framework.views import APIView
from rest_framework.response import Response
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph
from ..models import Meeting, Conversation
from django.db.models import Q
from langchain_community.llms import Cohere
from langchain.prompts import PromptTemplate



class MeetingNotificationView(APIView):

    def get_tomorrows_meetings(self):
        """Fetch meetings scheduled for tomorrow."""
        tomorrow = timezone.now().date() + timedelta(days=1)
        meetings = Meeting.objects.filter(datetime__date=tomorrow).select_related("person")
        return meetings

    #ver si esto es necesario
    def format_meeting_data(self, meetings):
        """Format meetings into a dictionary."""
        return [
            {
                "person_name": f"{meeting.person.first_name} {meeting.person.last_name}",
                "phone_number": meeting.person.phone_number,
                "meeting_time": meeting.datetime.strftime("%H:%M"),
                "status": meeting.status,
            }
            for meeting in meetings
        ]

    def create_notification_graph(self):
        """Creates a LangGraph workflow for evaluating and sending WhatsApp messages."""

        def process_meetings(meetings):
            """Formats meeting data."""
            return [
                {
                    "person_name": f"{meeting['person_name']}",
                    "phone_number": meeting["phone_number"],
                    "meeting_time": meeting["meeting_time"],
                    "status": meeting["status"],
                    "text": f"Meeting with {meeting['person_name']} at {meeting['meeting_time']} ({meeting['status']})."
                }
                for meeting in meetings
            ]

        def fetch_previous_messages(data):
            """Fetches the last 10 messages for each person and attaches them to data."""
            for item in data:
                phone_number = item["phone_number"]

                # Retrieve last 10 outgoing messages for this phone number
                last_messages = (
                    Conversation.objects
                    .filter(Q(person__phone_number=phone_number) & Q(message_type="outgoing"))
                    .order_by("-created")[:10]
                    .values_list("message", flat=True)
                )

                item["last_messages"] = list(last_messages)

            return data


        def evaluate_need_to_send(new_message, last_messages):
            """
            Uses an LLM to determine whether a new WhatsApp message should be sent.
            
            - If the same or very similar message was sent recently, it may skip.
            - Otherwise, it may decide to send the message.
            
            Returns: True (send) or False (do not send).
            """

            llm = Cohere(model="command", temperature=0.2)

            prompt = PromptTemplate(
                input_variables=["new_message", "last_messages"],
                template=(
                    "You are analyzing a set of previous WhatsApp messages sent to a user. "
                    "Given the new message: '{new_message}', determine if it should be sent "
                    "considering these past messages: {last_messages}. "
                    "Return only 'True' if the message should be sent or 'False' if it should not."
                )
            )

            response = llm.invoke(prompt.format(new_message=new_message, last_messages=last_messages)).strip().lower()

            print("Last Messages:", last_messages)
            print("New Message:", new_message)
            print("LLM Decision:", response)

            return response == "true"

        def agent_decision(data):
            """Agent decides whether to send a WhatsApp message."""
            decisions = []
            for item in data:
                should_send = evaluate_need_to_send(item["text"], item["last_messages"])
                item["should_send"] = should_send
                decisions.append(item)
            return decisions

        def send_whatsapp_message(data):
            """Sends WhatsApp messages based on agent's decision."""
            responses = []
            for item in data:
                if item["should_send"]:
                    response = WhatsAppService.send_message(item["phone_number"], item["text"])
                    responses.append(response)
                else:
                    responses.append(f"Skipped message for {item['phone_number']} (already notified).")
            return responses

        # Define workflow
        workflow = StateGraph(dict)
        
        workflow.add_node("process_meetings", RunnableLambda(process_meetings))
        workflow.add_node("fetch_previous_messages", RunnableLambda(fetch_previous_messages))
        workflow.add_node("agent_decision", RunnableLambda(agent_decision))
        workflow.add_node("send_whatsapp_message", RunnableLambda(send_whatsapp_message))

        # Define flow
        workflow.add_edge("process_meetings", "fetch_previous_messages")
        workflow.add_edge("fetch_previous_messages", "agent_decision")
        workflow.add_edge("agent_decision", "send_whatsapp_message")

        workflow.set_entry_point("process_meetings")
        workflow.set_finish_point("send_whatsapp_message")

        return workflow.compile()

    def get(self, request):
        """Handles GET requests to notify users of tomorrow's meetings."""
        try:
            meetings = self.get_tomorrows_meetings()
            formatted_meetings = self.format_meeting_data(meetings)
            workflow = self.create_notification_graph()
            results = workflow.invoke(formatted_meetings)

            return Response({
                "message": "Successfully sent notifications",
                "notifications": results,
                "meeting_count": len(meetings),
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)





