import streamlit as st
from backend import chatbot , retrive_all_threads
from langchain.messages import HumanMessage
import uuid

def get_thread():
    thread_id=uuid.uuid4()
    return thread_id

def reset():
    new_thread_id=get_thread()
    st.session_state['thread_id']=new_thread_id
    add_thread(new_thread_id)
    st.session_state['message_history']=[] 

def add_thread(thread_id):
     if thread_id not in st.session_state['chat_threads']:
          st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
     return chatbot.get_state(config={'configurable':{'thread_id':thread_id}}).values['message']


if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]

if 'thread_id' not in st.session_state:
     st.session_state['thread_id']=get_thread()

if 'chat_threads' not in st.session_state:
     st.session_state['chat_threads']=retrive_all_threads()

add_thread(st.session_state['thread_id'])

st.sidebar.title('My Chatbot')

if st.sidebar.button('New Coversation'):
     reset()

st.sidebar.header('All Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id']=thread_id
        messages=load_conversation(thread_id)

        temp_messages=[]

        for msg in messages:
            if isinstance(msg , HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role' : role , 'content' : msg.content})
        st.session_state['message_history']=temp_messages
         



for message in st.session_state['message_history']:
     with st.chat_message(message['role']):
          st.text(message['content'])


user_input=st.chat_input('Type here.....')

if user_input:

        st.session_state['message_history'].append({'role':'user' , 'content':user_input})
        with st.chat_message('user'):
            st.text(user_input)

        Configuration={
             'configurable':{'thread_id':st.session_state['thread_id']},
             'metadata':{
                  'thread_id':st.session_state['thread_id']
             },
             'run_name':'chat_turn'
        }
        
        with st.chat_message('assistant'):
                response=st.write_stream(
                      message_chunk.content for message_chunk , metadata in chatbot.stream(
                            {'message': [HumanMessage(content=user_input)]},
                            config=Configuration,
                            stream_mode='messages'
                      )
                )
        st.session_state['message_history'].append({'role':'assistant' , 'content':response})
    