from langgraph.graph import StateGraph , START ,END
from langchain_groq import ChatGroq
from typing import TypedDict,Annotated
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage , HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()


llm=ChatGroq(
    model='openai/gpt-oss-20b',
    temperature=0.3
)

class LLMstate(TypedDict):

    message: Annotated[list[BaseMessage] , add_messages]

def chatbot(state:LLMstate)->LLMstate:

    prompt=state['message']
    response=llm.invoke(prompt)

    return {'message': [response]}

conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)

checkpoint=SqliteSaver(conn=conn)

graph=StateGraph(LLMstate)

graph.add_node('chatbot' , chatbot)

graph.add_edge(START,'chatbot')
graph.add_edge('chatbot',END)


chatbot=graph.compile(checkpointer=checkpoint)

threads=set()

def retrive_all_threads():
    for check in checkpoint.list(None):
        threads.add(check.config['configurable']['thread_id'])

    return list(threads)
