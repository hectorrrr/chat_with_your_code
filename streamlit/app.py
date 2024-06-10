import streamlit as st
import json
import os

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
if 'metadata' not in st.session_state:
    st.session_state['metadata'] = load_metadata('./streamlit_metadata/users_conversations.json')


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
        for chat_name in st.session_state['metadata'][user_id].values():
            if st.button(chat_name, key=chat_name):
                st.session_state['active_chat'] = chat_name

    # Add a new chat section
    st.title("Add New Chat")
    new_chat_name = st.text_input("New Chat Name", key="new_chat_name")
    if st.button("Create Chat", key="create_new_chat"):
        if new_chat_name and new_chat_name not in st.session_state['metadata'][user_id].values():
            add_conversation(user_id=user_id,conversation_name=new_chat_name)
            st.rerun()
        else:
            st.error("Please enter a unique chat name.")

def create_chatbot():

    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)
        response = prompt
        st.chat_message("assistant").write(response)

if user_id:
    # Active chat handling
    if 'active_chat' not in st.session_state:
        try:
            st.session_state['active_chat'] = list(st.session_state['metadata'][user_id].keys())[0]
        except:
            st.write("Create a new chat to start the process")
    # Display the active chat messages
    st.header(f"Messages in {st.session_state['active_chat']}")


    app = create_chatbot()
else:
    st.write("Specify a User")
