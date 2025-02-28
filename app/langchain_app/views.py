import os
from django.http import JsonResponse
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_community.llms import Cohere

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# llm = OpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0.7)
# memory = ConversationBufferMemory()
# conversation = ConversationChain(llm=llm, memory=memory)

# Initialize OpenAI chat models for gpt-3.5-turbo (free tier)
# gpt35_chat = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0)

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Initialize LangChain components with Cohere
llm = Cohere(temperature=0.7)
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)

# Django view for LangChain conversation endpoint
def conversation_view(request):
    user_input = request.GET.get("message", "")
    if not user_input:
        return JsonResponse({"error": "Please provide a message."}, status=400)
    
    # Process the user's input through LangChain
    response = conversation.run(user_input)
    return JsonResponse({"response": response})


# Django view for GPT-3.5 invocation endpoint
def invoke_view(request):
    user_input = request.GET.get("message", "")
    if not user_input:
        return JsonResponse({"error": "Please provide a message."}, status=400)
    
    # Use the Cohere model to generate a response
    response = llm.predict(user_input)
    return JsonResponse({"response": response})
