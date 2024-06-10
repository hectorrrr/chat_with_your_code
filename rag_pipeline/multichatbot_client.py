"""
In this file we define a client that uses the LCEL (LangChain Expression Language)
methodology to define a conversation pipeline. In this way, the method is more customizable,
allowing to evaluate and trace each component separately.
"""
import os
import sys
from pathlib import Path
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import ConfigurableFieldSpec
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI


# Add the root folder to sys.path
root_path = Path(__file__).parent.parent  # Adjust according to actual path
sys.path.append(str(root_path))

print("Path--->", root_path)

## Import functionalities to setUp RAG pipeline:
from services.handler_memory import create_session_factory
## Import services
from operator import itemgetter
from dotenv import load_dotenv

_ = load_dotenv()  # take environment variables from .env.
print("key------->",os.getenv("OPENAI_API_KEY"))

class QA_Rag:
    """
    Class for managing RAG (Retrieval-Augmented Generation) system.
    """
    def __init__(
            self,
            user_id,
            conversation_id,
            config_path=None
            ):
        """
        Initialize the RAG system with retriever and LLM
        """
        # Initialize all resources:
        # Retriever
        # self.memory = ConversationBufferMemory()
        # self.embeddings = initializer.get_embeddings()
        self.prompts = ChatPromptTemplate.from_messages(
            [
                ("system", "You're an assistant by the name of Bob."),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),

            ]
        )
        # self.db = initializer.get_vector_db()
        self.llm = ChatOpenAI()
        # self.output_parser =  StrOutputParser()
        self.rag_chain = self.set_rag_pipeline()
        self.user_id = user_id
        self.conversation_id = conversation_id


    def initialize_message_history(self):

        ## Do things
        return None

 
    def handle_message_history(self,session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store :
            self.store [session_id] = ChatMessageHistory()
        return self.store[session_id]



    
    def set_rag_pipeline(self):

        chain = self.prompts | self.llm
        ## Involve memory around this chain:
        with_message_history = RunnableWithMessageHistory(
            # itemgetter("input") | chain,
            chain,
            create_session_factory("chat_historial"),
            input_messages_key="input",
            history_messages_key="history",
            history_factory_config = [
                ConfigurableFieldSpec(
                    id= "user_id",
                    annotation = str,
                    name = "User ID",
                    description="Unique identifier for the user",
                    default = "",
                    is_shared=True,
                ),
                ConfigurableFieldSpec(
                    id= "conversation_id",
                    annotation = str,
                    name = "Conversation ID",
                    description="Unique identifier for the conversation",
                    default = "",
                    is_shared=True,
                ),

            ]
        )

    
        return with_message_history

    def invoke_rag(self, user_query):

        return self.rag_chain.invoke(
            {"input": user_query},
            config={"configurable": {"user_id": self.user_id, "conversation_id":self.conversation_id}}, #,'callbacks': [ConsoleCallbackHandler()]
        )