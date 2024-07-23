import streamlit as st
import json
import os
import sys
import hashlib 
from pathlib import Path
from utils.chatbot import Chatbot


# Add the root folder to sys.path
root_path = Path(__file__).parent.parent  # Adjust according to actual path
sys.path.append(str(root_path))
from rag_pipeline.multichatbot_client import QA_Rag

def load_metadata(filename):
    """Load JSON data from a file and return as a dictionary."""
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("The file was not found.")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return {}



# Initialize session state for user data and conversations if not already present
current_active_chat = None ## TOBE IMPROVED
if 'metadata' not in st.session_state:
    st.session_state['metadata'] = load_metadata('./streamlit_metadata/users_conversations.json')

## Initialize a dictionary of clients for each chat in memory:
if 'chat' not in st.session_state:
    st.session_state.chat = {}

# Define once only the assistant:
if 'assistants' not in st.session_state:

    st.session_state.assistants = {}


if 'conversation_cache' not in st.session_state:
    st.session_state.conversation_cache = {}

def update_user_conversations():
    """Function to reload and update in the local 
    file the conversation status
    """
    print("Creating metadata file")
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
    if conversation_name not in user_data.values():
        st.session_state['metadata'][user_id] = {**st.session_state['metadata'][user_id],  str(len(user_data.keys()) + 1): conversation_name}

    update_user_conversations()


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


    user_id = st.text_input("Enter User ID")
    load_user_button = st.button("Load User")

    # Load or create user data
    if load_user_button and user_id:
        user_data = get_or_create_user_metadata(user_id)
        st.session_state['active_user'] = user_id  # Set the active user in session state
        st.success(f"Loaded data for User ID: {user_id}")

    if user_id:

        st.title("Chats")
        # st.session_state.conversation_cache[user_id] = {}
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


if user_id:
    if user_id not in st.session_state.chat:
        st.session_state.chat[user_id] = {}
        st.session_state.assistants[user_id] = {}


    # Define an assistant for that chat (if not exist)
    if st.session_state['active_chat'] not in st.session_state.assistants[user_id]:
        try:
            st.session_state.assistants[user_id][st.session_state['active_chat']] = QA_Rag(user_id=user_id, conversation_id = st.session_state['active_chat'])
            st.write("Session",st.session_state.assistants[user_id][st.session_state['active_chat']].store)
        except:
            st.write("Create a new chat to start the process")

    # Display the active chat messages
    st.header(f"Messages in {st.session_state['active_chat']}")
    # Active chat handling
    if 'active_chat' not in st.session_state or st.session_state['active_chat'] not in st.session_state.chat[user_id] or current_active_chat!=st.session_state['active_chat']:
        try:
            current_active_chat = st.session_state['active_chat']
            #st.session_state['active_chat'] = list(st.session_state['metadata'][user_id].keys())[0]
            st.session_state.chat[user_id][st.session_state['active_chat']] = Chatbot(
                                                                    user_id=user_id, 
                                                                    conversation_id = st.session_state['active_chat'],
                                                                    previous_messages = st.session_state.assistants[user_id][st.session_state['active_chat']].rag_chain.get_session_history(
                                                                                                                user_id=user_id,
                                                                                                                conversation_id = st.session_state['active_chat']).messages
                                                                                                                
                                                                                    )
            st.write(st.session_state.chat[user_id])
        except Exception as error:
            st.write(error)
            st.write("Create a new chat to start the process")

    
    
        

    st.session_state.chat[user_id][st.session_state['active_chat']].run()
else:
    st.write("Specify a User")
