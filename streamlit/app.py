import streamlit as st
import streamlit.components.v1 as components
import json
import os
import sys
import hashlib 
from pathlib import Path
from utils.chatbot import Chatbot

import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# URL for the Dash app
DASH_APP_URL = "http://localhost:8050"  # Replace with your Dash app's URL

# Page 2: View Graph
def page_view_graph():
    # Inject CSS to center the iframe
    st.markdown(
        """
        <style>
        .iframe-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 0;
            margin: 0;
        }
        .streamlit-expanderHeader {
            padding: 0;  /* Removes padding from the expander header */
        }
        </style>
        """, unsafe_allow_html=True
    )

    # Create a centered div for the iframe
    st.markdown('<div class="iframe-container">', unsafe_allow_html=True)
    components.iframe(DASH_APP_URL, width=1400, height=1000)
    st.markdown('</div>', unsafe_allow_html=True)
    


# Add the root folder to sys.path
root_path = Path(__file__).parent.parent  # Adjust according to actual path
sys.path.append(str(root_path))
from src.rag_pipeline.multichatbot_client import QA_Rag




def load_metadata(filename):
    """Load JSON data from a file and return as a dictionary."""
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        logging.error("The file was not found.")
        return {}
    except json.JSONDecodeError:
        logging.error("Error decoding JSON.")
        return {}



# Initialize session state for user data and conversations if not already present
current_active_chat = None ## TOBE IMPROVED
if 'metadata' not in st.session_state:
    st.session_state['metadata'] = load_metadata('./streamlit_metadata/users_conversations.json')

## Initialize a dictionary of clients for each chat in memory:
if 'chat' not in st.session_state:
    st.session_state.chat = {}

if 'last_selected' not in st.session_state:
    st.session_state.last_selected = "home"

# Define once only the assistant:
if 'assistants' not in st.session_state:

    st.session_state.assistants = {}

if 'active_chat'  not in st.session_state:
    st.session_state['active_chat'] = None


if 'conversation_cache' not in st.session_state:
    st.session_state.conversation_cache = {}

def update_user_conversations():
    """Function to reload and update in the local 
    file the conversation status
    """
    logging.debug("Creating metadata file")
    os.makedirs(
        os.path.dirname(
            './streamlit_metadata/users_conversations.json'),
            exist_ok=True
        )

    # Optionally, you can save this to a file (uncomment to use):
    with open('./streamlit_metadata/users_conversations.json', 'w') as f:
        json.dump(st.session_state['metadata'], f, indent=4)

def create_chat_id(chat_name):
    """This function, given a chat name
    generates a unique hash identifier for it

    Args:
        chat_name (str): Name of the chat

    Returns:
        Str: Hash of the chat
    """
    hash_object = hashlib.sha256(chat_name.encode())
    hash_hex = hash_object.hexdigest()
    hash_hex[0:10]
# Function to retrieve or create user metadata
def get_or_create_user_metadata(user_id):
    """Add a new conversation to the session state

    Args:
        user_id (str): Id of the user for the current session

    Returns:
        Dict: All conversations for the specified user.
    """
    logging.info("Updating conversations for User_ID")
    if user_id not in st.session_state['metadata'].keys():
        # Initialize with empty metadata and conversation list
        st.session_state['metadata'][user_id] = {}
        update_user_conversations()
    return st.session_state['metadata'][user_id]


# Function to add a new conversation to a user
def add_conversation(user_id, conversation_name):
    """Add a new conversation to the session state and register it
    to the local file system.

    Args:
        user_id (_type_): _description_
        conversation_name (_type_): _description_
    """
    user_data = get_or_create_user_metadata(user_id)
    logging.info(f"Retrieved user data----> {user_data}")

    # If the conversation is new add it
    if conversation_name not in user_data.values():
        st.session_state['metadata'][user_id] = {**st.session_state['metadata'][user_id],  str(len(user_data.keys()) + 1): conversation_name}

    update_user_conversations()



## Floating buttons
if 'last_selected' not in st.session_state:
    st.session_state['last_selected'] = 'home'  # Default state





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
