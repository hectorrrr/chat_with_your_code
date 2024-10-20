# session_utils.py
import json
import os
import hashlib
import logging
import streamlit as st

def init_session_state(key, default_value):
    """Initialize a key in the session state if it does not exist."""
    if key not in st.session_state:
        st.session_state[key] = default_value


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

def update_user_conversations():
    """Function to reload and update the conversation status."""
    logging.debug("Creating metadata file")
    os.makedirs(os.path.dirname('./streamlit_metadata/users_conversations.json'), exist_ok=True)

    with open('./streamlit_metadata/users_conversations.json', 'w') as f:
        json.dump(st.session_state['metadata'], f, indent=4)

def create_chat_id(chat_name):
    """Generates a unique hash identifier for a chat."""
    hash_object = hashlib.sha256(chat_name.encode())
    return hash_object.hexdigest()[0:10]

def get_or_create_user_metadata(user_id):
    """Add a new conversation to the session state."""
    logging.info("Updating conversations for User_ID")
    if user_id not in st.session_state['metadata']:
        st.session_state['metadata'][user_id] = {}
        update_user_conversations()
    return st.session_state['metadata'][user_id]

def add_conversation(user_id, conversation_name):
    """Add a new conversation to the session state and register it to the local file system."""
    user_data = get_or_create_user_metadata(user_id)
    logging.info(f"Retrieved user data----> {user_data}")

    if conversation_name not in user_data.values():
        st.session_state['metadata'][user_id][str(len(user_data) + 1)] = conversation_name

    update_user_conversations()
