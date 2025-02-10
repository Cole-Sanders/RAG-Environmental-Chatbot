import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API key
API_KEY = os.getenv("API_KEY")


st.markdown(
    """
    <style>
        /* Background Color */
        .stApp {
            background-color: #f5f7f4;
        }

        /* Chat Title */
        .stMarkdown h1 {
            color: #333333;
            font-weight: bold;
        }

        /* Chat Input Field */
        .stChatInputContainer {
            background-color: #e3ede4 !important;
            border: 2px solid #5c7063 !important;
            border-radius: 10px;
        }

        /* Chat Messages */
        .stChatMessage {
            background-color: #dbe6d5;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 8px;
            color: #333333;
        }

        /* User Chat Message (red background) */
        .stChatMessageUser {
            background-color: #e57373 !important;
            color: white !important;
        }

        /* Assistant Chat Message (light yellow background) */
        .stChatMessageAssistant {
            background-color: #fdd835 !important;
            color: #333333 !important;
        }

        /* Chat Input Box */
        .stChatInputContainer textarea {
            color: #333333 !important;
            background-color: #e3ede4 !important;
            border-radius: 8px !important;
            padding: 10px !important;
        }

        /* Chat Submit Button */
        .stButton>button {
            background-color: #5c7063;
            color: white;
            border-radius: 10px;
            padding: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit App Title
st.title("EcoValid")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Chat with Eco..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Make an API request using the API key (Example usage)
    response = f"Eco: {prompt}"  # Placeholder response

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})