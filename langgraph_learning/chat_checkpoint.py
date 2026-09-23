from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.mongodb import MongoDBSaver
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



graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)


graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# graph = graph_builder.compile()

def compile_graph_with_checkpointer(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)


DB_URL ="mongodb://admin:admin@localhost:27017"
with  MongoDBSaver.from_conn_string(DB_URL) as checkpointer:
    graph_with_checkpointer = compile_graph_with_checkpointer(checkpointer=checkpointer)

    config = {
        "configurable":{
            "thread_id": "nishant"
        }
    }

    for chunck in graph_with_checkpointer.stream(
        State({"message":["what am I learning?"]}),
        config=config,
        stream_mode="values"
        ):
            chunck["message"][-1].pretty_print()

