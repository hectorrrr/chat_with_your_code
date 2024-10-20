import streamlit as st
 
import pathlib
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class Chatbot:
    def __init__(self, user_id, conversation_id,previous_messages):

        self.user_id = user_id
        self.conversation_id = conversation_id
 
        if "chat_ready" not in st.session_state:
            st.session_state["chat_ready"] = False

        if "disable_new" not in st.session_state:
            st.session_state["disable_new"] = False
 
        if "start" not in st.session_state:
            st.session_state["start"] = True


        logging.debug(f'Messages in session_state:{"messages" in st.session_state}')
        if not  st.session_state.messages:
            if previous_messages:
                logging.info(f"Reloading conversation with {previous_messages}")
                self.reload_conversation(previous_messages)
            else:
                st.session_state.messages = [
                    {"role": "assistant", "content": "I'm an AI assistant, how can I help?"}
                ]

        
    def reload_conversation(self,previous_messages):
        """_summary_

        Args:
            previous_messages (_type_): _description_
        """
        st.session_state.messages =  []
        for msg in previous_messages:
            st.session_state.messages.append(
                {"role": msg.type, "content": msg.content})

    def create_chatbot(self):
        # st.markdown(f"## Dossier patient:`{st.session_state.patient_id}`")

        logging.info("Created chatbot")
        logging.info(f"Rewritting {st.session_state.messages}")
        for msg in st.session_state.messages:
            logging.info("rewritting conversation")
            st.chat_message(msg["role"]).write(msg["content"])
 
        if prompt := st.chat_input():
            st.session_state.messages.append(
                {"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
 
            with st.spinner("Writing..."):
                if st.session_state.assistants[self.user_id][self.conversation_id]:
                    # st.write("Chat history--->", st.session_state.assistants[self.user_id][self.conversation_id].rag_chain.get_session_history(user_id="hlopezpe", conversation_id = self.conversation_id))
                    response = {
                        # "answer": rag_client.invoke_rag({'question':prompt,'chat_history':st.session_state.messages}
                        "answer": st.session_state.assistants[self.user_id][self.conversation_id].invoke_rag(prompt
                        )
                    }
                else:
                    response = {
                        # "answer": rag_client.invoke_rag({'question':prompt,'chat_history':st.session_state.messages}
                        "answer": "Load an LLM"
                    }
                    
 
            msg = {"content": response["answer"].content, "role": "assistant"}
            st.session_state.messages.append(msg)
 
            st.chat_message("assistant").write(response["answer"].content)
 

    def run(self):
        self.create_chatbot()
