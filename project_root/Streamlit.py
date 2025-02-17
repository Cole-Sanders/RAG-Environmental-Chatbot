import streamlit as st
import os
from dotenv import load_dotenv
from litellm import completion

# Set page title and favicon
st.set_page_config(page_title="EcoValid", page_icon="🌿")

# Load environment variables
load_dotenv()

# Function to access the API with memory support
def model_4o(enquire):
    # Retrieve stored conversation history from session state
    messages = st.session_state.conversation_memory

    # Append new user message
    messages.append({"role": "user", "content": enquire})

    response = completion(
        api_key=os.getenv("API_KEY"),
        base_url="http://18.216.253.243:4000/",
        model="gpt-4o",
        custom_llm_provider="openai",
        messages=messages
    )
    
    # Append assistant response to memory
    assistant_response = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": assistant_response})

    return assistant_response

# Load external CSS
def load_css(file_name):
    with open(file_name, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Load CSS file
load_css("frontend/pages/styles.css")

# Streamlit App Title
st.title("EcoValid")

# Initialize session state for role selection
if "role" not in st.session_state:
    st.session_state.role = "Select an option"

# Initialize session state for conversation memory
if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = []  # Stores conversation history

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
        st.session_state.conversation_memory = []  # Reset memory when role changes
        st.rerun()

# Display chat messages from memory
for message in st.session_state.conversation_memory:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"<p style='margin:0; padding:10px;'>{message['content']}</p>", unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar="frontend/bot_icon.png"):
            st.markdown(f"<div class='assistant-message'>{message['content']}</div>", unsafe_allow_html=True)

# Handle user input
if st.session_state.role != "Select an option":
    if prompt := st.chat_input("Chat with Eco..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(f"<p style='margin:0; padding:10px;'>{prompt}</p>", unsafe_allow_html=True)

        # Add user message to conversation memory
        st.session_state.conversation_memory.append({"role": "user", "content": prompt})

        # Create a placeholder for assistant response
        response_placeholder = st.empty()

        with st.chat_message("assistant", avatar="frontend/components/bird.jpg"):
            spinner_placeholder = st.markdown("<div class='loader'></div> Generating...", unsafe_allow_html=True)

            # Generate response with memory support
            response = model_4o(prompt)

            spinner_placeholder.empty()
            response_placeholder.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)

        # Add assistant response to memory
        st.session_state.conversation_memory.append({"role": "assistant", "content": response})
