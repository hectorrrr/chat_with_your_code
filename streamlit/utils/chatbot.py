import streamlit as st
 
import pathlib
import sys


#from src.rag_pipeline.chatbot_seq_chain_qa_pipeline import QA_Rag

 

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
 
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "assistant", "content": "I'm an AI assistant, how can I help?"}
            ]

        if previous_messages:
            self.reload_conversation(previous_messages)

    def reload_conversation(self,previous_messages):
        """_summary_

        Args:
            previous_messages (_type_): _description_
        """
        for msg in previous_messages:
            st.session_state.messages.append(
                {"role": msg.type, "content": msg.content})
            # st.chat_message(msg.type).write(msg.content)
 
    def create_chatbot(self):
        # st.markdown(f"## Dossier patient:`{st.session_state.patient_id}`")
        for msg in st.session_state.messages:
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
                        "answer": "Load an LLM crack"
                    }
                    
 
            msg = {"content": response["answer"].content, "role": "assistant"}
            st.session_state.messages.append(msg)
 
            st.chat_message("assistant").write(response["answer"].content)
 
    def send_question(self, question):
        with st.spinner("Writing..."):
            st.write("Chat history--->", st.session_state.assistants[self.user_id][self.conversation_id].rag_chain.get_session_history(user_id=self.user_id, conversation_id = self.conversation_id))
            response = {
                # "answer": rag_client.invoke_rag({'question':question,'chat_history':st.session_state.messages}
                    "answer": st.session_state.assistants[self.user_id][self.conversation_id].invoke_rag(      question     
                )
            }
 
            
 
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append(
            {"role": "assistant", "content": response["answer"]}
        )

    def run(self):
        # self.create_sidebar()
 
        # if st.session_state.chat_ready:
        self.create_chatbot()
        # else:
        #     self.default_chatbot()
            # make_footer(st, ASSETS_PATH, n_lines=2)