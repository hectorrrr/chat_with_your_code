
import streamlit as st
import streamlit.components.v1 as components


DASH_APP_URL = "http://localhost:8050"


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
    