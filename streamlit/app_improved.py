import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


import streamlit as st
import sys
from pathlib import Path
from utils.chatbot import Chatbot
from utils.session_utils import load_metadata, get_or_create_user_metadata, add_conversation, init_session_state
from utils.streamlit_utils import page_view_graph








# Add the root folder to sys.path
root_path = Path(__file__).parent.parent  # Adjust according to actual path
sys.path.append(str(root_path))
from src.rag_pipeline.multichatbot_client import QA_Rag





# Initialize session state for user data and conversations if not already present
current_active_chat = None # TOBE IMPROVED


# Initialize session state using the helper function
init_session_state('metadata', load_metadata('./streamlit_metadata/users_conversations.json'))
init_session_state('chat', {})
init_session_state('last_selected', 'home')
init_session_state('assistants', {})
init_session_state('active_chat', None)
init_session_state('conversation_cache', {})



# Styling for the sidebar and buttons
st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    border-radius: 10px;
    border: 1px solid #f63366;
    color: #f63366;
}
</style>
""", unsafe_allow_html=True)


# Sidebar for chat session selection and adding new chats
with st.sidebar:

        # Top navigation buttons
    st.markdown('<div class="top-buttons">', unsafe_allow_html=True)
    
     # Display the buttons based on the current state
    if st.session_state['last_selected'] == 'home':
        if st.button("View Knowledge Graph", key='view_graph'):
            st.session_state['last_selected'] = 'graph'
    else:
        if st.button("View Chats Page", key='chats_page'):
            st.session_state['last_selected'] = 'home'

    

    user_id = st.text_input("Enter User ID")
    load_user_button = st.button("Load User")

    # Load or create user data
    if load_user_button and user_id:
        user_data = get_or_create_user_metadata(user_id)
        st.session_state['active_user'] = user_id  # Set the active user in session state
        # st.write(f"Active user {user_id}")
        st.success(f"Loaded data for User ID: {user_id}")

    if user_id:

        st.title("Chats")
        for chat_id, chat_name in st.session_state['metadata'][user_id].items():
            if st.button(chat_name, key=chat_name):
                ## If a new chat is selected reset the messages
                st.session_state.messages = []
                st.session_state['active_chat'] = chat_id


    # Add a new chat section
    st.title("Add New Chat")
    new_chat_name = st.text_input("New Chat Name", key="new_chat_name")
    if st.button("Create Chat", key="create_new_chat"):
        if new_chat_name and new_chat_name not in st.session_state['metadata'][user_id].values():
            add_conversation(user_id=user_id,conversation_name=new_chat_name)
            st.rerun()
        else:
            st.error("Please enter a unique chat name.")

    
## To be replaced:
if st.session_state['last_selected']=="graph":
    # Call the graph page function when button is clicked
    page_view_graph()
else:
    ## Define main page
    # Create a full-width header
    st.markdown("""
        <style>
            .full-width-header {
                background-color: #F63366;
                padding: 20px;
                border-radius: 10px;
                width: 100%;
                margin-left: 0px;
                margin-right: 0px;
                text-align: center;
            }
            .full-width-header h1, .full-width-header h4 {
                color: white;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
            }
        </style>
        <div class="full-width-header">
            <h2>Welcome to 'Chat with Your Code' 🚀</h2>
            <h4>Increase your performance with code reproducibility</h4>
        </div>
        """, unsafe_allow_html=True)
    if user_id:
        if user_id not in st.session_state.chat or user_id not in st.session_state.assistants:
            st.session_state.chat[user_id] = {}
            st.session_state.assistants[user_id] = {}
            # st.write(f"Assistants---> {st.session_state.assistants[user_id]}")


        # Define an assistant for that chat (if not exist)
        if st.session_state['active_chat'] not in st.session_state.assistants[user_id]:
            try:
                st.session_state.assistants[user_id][st.session_state['active_chat']] = QA_Rag(user_id=user_id, conversation_id = st.session_state['active_chat'])
                # st.write("Session",st.session_state.assistants[user_id][st.session_state['active_chat']].store)
            except Exception as error:
                st.write(f"Create a new chat to start the process {error}")


        # Active chat handling
        if not st.session_state['active_chat'] or st.session_state['active_chat'] not in st.session_state.chat[user_id] or current_active_chat!=st.session_state['active_chat']: 
            ## Maybe I can remove the last condition so no chatbot is reloaded
            try:
                current_active_chat = st.session_state['active_chat']
                
                logging.info(f"""Previous messages {st.session_state.assistants[user_id][st.session_state['active_chat']].rag_chain.get_session_history(
                                                                                                                    user_id=user_id,
                                                                                                                    conversation_id = st.session_state['active_chat']).messages}""")

                st.session_state.chat[user_id][st.session_state['active_chat']] = Chatbot(
                                                                        user_id=user_id, 
                                                                        conversation_id = st.session_state['active_chat'],
                                                                        previous_messages = st.session_state.assistants[user_id][st.session_state['active_chat']].rag_chain.get_session_history(
                                                                                                                    user_id=user_id,
                                                                                                                    conversation_id = st.session_state['active_chat']).messages
                                                                                                                        
                                                                                            )
                # st.write(st.session_state.chat[user_id])
            except Exception as error:
                # st.write(error)
                st.write("Create or Select a chat to start the process")

        
        
        if st.session_state['active_chat']:  
            st.session_state.chat[user_id][st.session_state['active_chat']].run()
    else:
        # Optional: Add a subtitle or description below the header
        st.subheader("Specify a User to start the conversation")
