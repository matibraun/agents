from rest_framework.response import Response
from rest_framework.decorators import api_view
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from ..models import Person, Meeting, Conversation
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from langchain_community.llms import Cohere
from langchain.prompts import PromptTemplate
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from ..services import WhatsAppService

@csrf_exempt
@api_view(['POST'])
def whatsapp_response(request):
    """Handles incoming WhatsApp messages and routes them to the correct agent."""
    
    phone_number = request.POST.get("From", "").replace("whatsapp:", "")
    user_message = request.POST.get("Body", "").strip()

    if not phone_number or not user_message:
        return Response({"error": "Invalid request data"}, status=400)

    def classify_message(state):
        """Classifies the incoming message type."""
        llm = Cohere(model="command", temperature=0.3)
        prompt = PromptTemplate(
            input_variables=["message"],
            template=(
                "A user sent this message: '{message}'. Classify it as one of the following: "
                "'meeting_confirmation', 'reschedule', 'product_info', 'purchase_request'. "
                "Return only the classification."
            )
        )
        classification = llm.invoke(prompt.format(message=state["message"])).strip()

        print("Classification: ", classification)

        return {**state, "classification": classification}

    def handle_meeting_management(state):
        """Handles confirmation/cancellation of a meeting."""
        person = Person.objects.get(phone_number=state["phone_number"])
        meeting = Meeting.objects.filter(person=person, datetime__gte=timezone.now()).first()
        if meeting:
            if "confirm" in state["message"].lower():
                meeting.status = "confirmed"
            elif "cancel" in state["message"].lower():
                meeting.status = "cancelled"
            meeting.save()
        return {**state, "response": f"Meeting status updated to {meeting.status}"}

    def handle_reschedule(state):
        """Handles rescheduling and provides a Calendly link."""
        person = Person.objects.get(phone_number=state["phone_number"])
        meeting = Meeting.objects.filter(person=person, datetime__gte=timezone.now()).first()
        if meeting:
            meeting.status = "rescheduled"
            meeting.save()
        return {**state, "response": "Your meeting has been rescheduled. Please select a new time: https://mocked-calendly.com"}
    
    def handle_product_info(state):
        """Handles product inquiries by providing details from a document."""
        return {**state, "response": "Here is the product information: [Mocked PDF Response]"}

    def handle_purchase(state):
        """Handles purchase requests by providing a payment link."""
        return {**state, "response": "Here is your payment link: https://mocked-payment.com"}

    def send_whatsapp_message(state):
        """Sends a WhatsApp message back to the user."""
        phone_number = state["phone_number"]
        response_message = state.get("response", "No response available")
        
        WhatsAppService.send_message(phone_number, response_message)
        
        return state

    workflow = StateGraph(dict)

    workflow.add_node("classify_message", RunnableLambda(classify_message))
    workflow.add_node("meeting_management", RunnableLambda(handle_meeting_management))
    workflow.add_node("reschedule", RunnableLambda(handle_reschedule))
    workflow.add_node("product_info", RunnableLambda(handle_product_info))
    workflow.add_node("purchase", RunnableLambda(handle_purchase))
    workflow.add_node("send_message", RunnableLambda(send_whatsapp_message))

    workflow.add_conditional_edges(
        "classify_message",
        lambda state: state["classification"],
        {
            "meeting_confirmation": "meeting_management",
            "reschedule": "reschedule",
            "product_info": "product_info",
            "purchase_request": "purchase",
        }
    )

    workflow.add_edge("meeting_management", "send_message")
    workflow.add_edge("reschedule", "send_message")
    workflow.add_edge("product_info", "send_message")
    workflow.add_edge("purchase", "send_message")

    workflow.set_entry_point("classify_message")
    workflow.set_finish_point("send_message")

    compiled_workflow = workflow.compile()
    result = compiled_workflow.invoke({"phone_number": phone_number, "message": user_message})
    
    try:
        person = Person.objects.get(phone_number=phone_number)
        Conversation.objects.create(person=person, message=user_message, message_type="incoming")
    except ObjectDoesNotExist:
        return Response({"error": "Person not found"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({"response": result.get("response", "No response available")}, status=status.HTTP_200_OK)
