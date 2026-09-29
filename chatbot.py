from langgraph.graph import StateGraph , START ,END 
from langchain_groq import ChatGroq
from typing import TypedDict,Annotated
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage , HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_mcp_adapters.client import MultiServerMCPClient
import sqlite3
import os
import asyncio

load_dotenv()

llm=ChatGroq(
    model='openai/gpt-oss-20b',
    temperature=0.3
)

mcp=MultiServerMCPClient({
    "Myserver":{
        'transport':'streamable_http',
        'url':'https://my-ai-server.fastmcp.app/mcp',
        'headers':{
            'Authorization':f'Bearer {os.getenv('fmcp_6xc3lbJOIhTzxlP75RulCUoyoLSXmmt6nKYILTJ9NLI')}'
        }
    }
})

search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}

tools=[search_tool , calculator]
llm_with_tools=llm.bind_tools(tools)

class LLMstate(TypedDict):

    message: Annotated[list[BaseMessage] , add_messages]

async def build_graph():

    tool1=await mcp.get_tools()

    llm_with_tools=llm.bind_tools(tool1)
    async def chatbot(state:LLMstate)->LLMstate:

        prompt=state['message']
        response=await llm_with_tools.ainvoke(prompt)
        return {'message': [response]}



    conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)

    checkpoint=SqliteSaver(conn=conn)
    tool_node = ToolNode(tools)
    graph=StateGraph(LLMstate)

    graph.add_node('chatbot' , chatbot)
    graph.add_node('tools' , tool_node)

    graph.add_edge(START,'chatbot')
    graph.add_conditional_edges('chatbot' , tools_condition)
    graph.add_edge('tools' , 'chatbot')


    chatbot=graph.compile(checkpointer=checkpoint)
    return chatbot


async def main():

    chatbot=await build_graph()

    response= await chatbot.ainvoke([HumanMessage(content='What is the condition of my pc')])
    print(response['message'][-1].content)


if __name__ == "__main__":

    asyncio.run(main())
