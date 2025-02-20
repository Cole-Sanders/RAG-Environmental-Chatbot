import streamlit as st
import os
from dotenv import load_dotenv
from litellm import completion

# Set page title and favicon
st.set_page_config(page_title="EcoValid", page_icon="🌿")  

# Load environment variables from .env file
load_dotenv()

# Function to access the azure api key and get a response from the model
def model_4o(enquire):

    # Retrieve stored conversation history
    messages = st.session_state.conversation_memory

    # Append new user message
    messages.append({"role": "user", "content": enquire})

    response = completion(
        api_key=os.getenv("API_KEY"),# your api key
        base_url="http://18.216.253.243:4000/",
        model="gpt-4o", #could be changed to any model you want
        custom_llm_provider="openai",
        messages=messages
    )
    
    # Append assistant response to history
    assistant_response = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": assistant_response})

    return assistant_response


# Function to load CSS from external file
def load_css(file_name):
    with open(file_name, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# Load external CSS
load_css("frontend/pages/styles.css")

# Streamlit App Title
st.title("EcoValid")

# Initialize session state for role selection
if "role" not in st.session_state:
    st.session_state.role = "Select an option"

# Initialize session state for conversation memory
if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = []  # Stores only the current conversation

# Always show role selector in the top-right corner
st.markdown(f'<div class="role-selector">Role: {st.session_state.role}</div>', unsafe_allow_html=True)

# Role selection dropdown in sidebar
with st.sidebar:
    role = st.selectbox(
        "Select a role:",
        ("Select an option", "Researcher", "Policy Maker"),
        index=("Select an option", "Researcher", "Policy Maker").index(st.session_state.role)
    )

    if role != st.session_state.role:
        st.session_state.role = role
        st.session_state.conversation_memory = []  # Reset conversation when role changes
        st.rerun()

# Display chat messages from memory
for message in st.session_state.conversation_memory:
    # with st.chat_message(message["role"]):
    #     st.markdown(f"<p style='margin:0; padding:10px;'>{message['content']}</p>", unsafe_allow_html=True)

    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"<p style='margin:0; padding:10px;'>{message['content']}</p>", unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar="frontend/components/bird.jpg"):  # Custom bot icon here
            st.markdown(f"<div class='assistant-message'>Eco: {message['content']}</div>", unsafe_allow_html=True)

# React to user input (only after role selection)
if st.session_state.role != "Select an option":
    if prompt := st.chat_input("Chat with Eco..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(f"<p style='margin:0; padding:10px;'>{prompt}</p>", unsafe_allow_html=True)

        # Generate response using updated function
        with st.chat_message("assistant", avatar="frontend/components/bird.jpg"):
            response_placeholder = st.empty()
            spinner_placeholder = st.markdown("<div class='loader'></div> Generating...", unsafe_allow_html=True)

            # Call function with memory support
            response = model_4o(prompt)

            spinner_placeholder.empty()
            response_placeholder.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)