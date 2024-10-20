"""
In this file we define a client that uses the LCEL (LangChain Expression Language)
methodology to define a conversation pipeline. In this way, the method is more customizable,
allowing to evaluate and trace each component separately.
"""
import os
import sys
import langchain
from pathlib import Path
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ChatMessageHistory
from langchain_community.vectorstores import Neo4jVector
from langchain_community.graphs import Neo4jGraph
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import ConfigurableFieldSpec
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings


# Add the root folder to sys.path
root_path = Path(__file__).parent.parent  # Adjust according to actual path
sys.path.append(str(root_path))


## Import functionalities to setUp RAG pipeline:
from services.handler_memory import create_session_factory
## Import services
from operator import itemgetter
from dotenv import load_dotenv

langchain.debug = True

_ = load_dotenv()  # take environment variables from .env.


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

        self.cypher_gen_prompt = PromptTemplate.from_template(
            """
            You are a Cypher language expert.
            Your Task:Generate Cypher statement to query a graph database.
            To better contextualize, the Graph database is mapping the Data Science implementations using python
            and is divided in the following entities:

            Instructions:
            Use only the provided relationship types and properties in the schema.
            Do not use any other relationship types or properties that are not provided.
            Schema:
            {schema}
            Note: Do not include any explanations or apologies in your responses.
            Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
            Do not include any text except the generated Cypher statement.
                - Data Preprocessing Area: Nodes labeled as 'Area' representing areas of Data Science, like 'Data Visualization' or 'Data Preprocessing'.
                - SubArea: Nodes labeled as 'SubArea' representing sub-areas within data preprocessing. This field is optional, some of the nodes may not have a relation with a 'SubArea' node, so generally 
                should not be added in the query.
                - Framework: Nodes labeled as 'Framework' representing frameworks used in data science.
                - Class: Nodes labeled as 'Class' representing a set of functions defining a Python class within a framework.
                - Function: Nodes labeled as 'Function' representing custom functions built on top of those frameworks.
            Nodes do not neccesarily have parents of each type of label.

            Your main focus should be to identify the Framework and the Function that is being asked.
            The question is:
            {question}
            """
            )
        
        self.prompt_handle_conver =  PromptTemplate.from_template("""
            You are a conversational chatbot, designed to answer based mainly in the context you are provided to the user questions.
            Questions are most likely related to coding doubts. You should provide code examples whenever possible, always including in your response
            the code functions from the context as they are not available to the user.
            Context: {context}

            User question: {input}
            """)
        self.prompt_summarise_conver =  PromptTemplate.from_template("""
            You are going to be provided with several consecutive messages of a user from a conversation, together with the current one.
            Your task is to contextualize the current message with anything crutial from the oldest if it is necessary, so it can be understood alone. 
            You should not change the format of the message and just create a final Input/question from the Current question, not older questions should be added.

            Also try to condense the information (without removing anything relevant) so the input is more usable as a query for a vector database.
                                                                    
            History of messages: {chat_history}
                                                                    
            Current message: {input_message}
                                                                    
            Final Message: 

            """)
        # self.db = initializer.get_vector_db()
        self.llm = ChatOpenAI()
        self.retriever = self.__set_retriever()
        self.graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password=os.environ['NEO4J_PASSWORD'],database='graphrag')
        # self.output_parser =  StrOutputParser()
        self.rag_chain = self.set_rag_pipeline()
        self.user_id = user_id
        self.conversation_id = conversation_id


    def context_unifier(self,full_context):
        print("Received Context---->",full_context)
        unified_context = full_context['graph_context'] + full_context['vector_context'] 
        return unified_context
    
    def get_schema(self,summarisation):
        return self.graph.get_schema
    
    def select_last_n_messages(self,chat_history,n=3):
        print(chat_history)
        if len(chat_history) <3:
            return chat_history
        else:
            print("Shortering chat messages")
            print(chat_history)
            print(chat_history[-3:])
            return chat_history[-3:]


    def run_cypher_query(self,query):
        try:
            print("Generated query---->",query.content)
            node_contents = self.graph.query(query.content)[:5]
            return node_contents
        except: 
            return ""
        
    def __set_retriever(self):
        database = "graphrag"  # default index name
        model_name = "sentence-transformers/all-MiniLM-L6-v2" # You can specify any sentence-transformer model from the hub
        embeddings = HuggingFaceEmbeddings(model_name=model_name)


        # The vector index name was assigned by default
        store = Neo4jVector.from_existing_index(
            embeddings,
            url=os.environ["NEO4J_URL"],
            username=os.environ["NEO4J_USERNAME"],
            password=os.environ["NEO4J_PASSWORD"],
            index_name="vector",
            search_type="hybrid",
            keyword_index_name="keyword",
            database=database
        )
        return store.as_retriever(search_kwargs= {'k':2, 'score_threshold':0.5})
    
    def set_rag_pipeline(self):
        graph_retriever_chain =  self.cypher_gen_prompt | self.llm | RunnableLambda(self.run_cypher_query)
        # In this case we also add the rephrasing/summarising from the history:
        summarisation_chain =  {"chat_history": itemgetter('history') | RunnableLambda(self.select_last_n_messages), "input_message": itemgetter('input')}| self.prompt_summarise_conver | self.llm | StrOutputParser()
        final_chain =  {'context' :summarisation_chain | {'graph_context': {'question': RunnablePassthrough(), 'schema': RunnableLambda(self.get_schema)} | graph_retriever_chain , 'vector_context':self.retriever} | RunnableLambda(self.context_unifier), 'input': itemgetter("input")} | self.prompt_handle_conver | self.llm
        
        with_message_history = RunnableWithMessageHistory(
            # itemgetter("input") | chain,
            final_chain,
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