from collections import OrderedDict
import logging
import streamlit as st

class RAGManager:
    def __init__(self, max_items=5):
        self.max_items = max_items
        
        # Ensure that both rag_instances and chat_instances are in Streamlit's session state
        if 'rag_instances' not in st.session_state:
            st.session_state.rag_instances = OrderedDict()
        if 'chat_instances' not in st.session_state:
            st.session_state.chat_instances = OrderedDict()

    def add_instance(self, instance_type, user_id, chat_id, instance):
        """Add a new instance (RAG or Chat) and enforce memory limit."""
        key = (user_id, chat_id)
        st.session_state[instance_type][key] = instance
        self._enforce_memory_limit(instance_type)

    def get_instance(self, instance_type, user_id, chat_id):
        """Retrieve an instance (RAG or Chat) from memory."""
        return st.session_state[instance_type].get((user_id, chat_id))

    def move_to_end(self, instance_type, user_id, chat_id):
        """Mark the instance as recently used."""
        key = (user_id, chat_id)
        st.session_state[instance_type].move_to_end(key, last=True)

    def _enforce_memory_limit(self, instance_type):
        """Enforce the memory limit by removing the least recently used instance."""
        instance_dict = st.session_state[instance_type]
        if len(instance_dict) > self.max_items:
            oldest_instance = next(iter(instance_dict))
            instance_dict.pop(oldest_instance)
            logging.info(f"Removed oldest {instance_type[:-1]} instance for {oldest_instance}")
