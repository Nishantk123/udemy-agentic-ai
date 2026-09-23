from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model

load_dotenv()

class State(TypedDict):
    message: Annotated[list, add_messages]

llm = init_chat_model(
    model="gpt-4.1-mini",
    model_provider="openai"
)
def chatbot(state:State):
    response = llm.invoke(state.get("message"))
    return {"message": response}

def samplenode(state:State):
    print("\n\nInside the sample node", state)
    return {"message" : ["Sample Message Appended"]}

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("samplenode", samplenode)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "samplenode")
graph_builder.add_edge("samplenode", END)

graph = graph_builder.compile()

updated_state = graph.invoke(State({"message":["Hi, My Name is Nishant Kashyap."]}))

print("\n\nupdated_state", updated_state)