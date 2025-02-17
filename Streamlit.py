import streamlit as st
import os
from dotenv import load_dotenv
from litellm import completion

# Load environment variables
load_dotenv()

# Function to access the API
def model_4o(enquire):
    response = completion(
        api_key=os.getenv("API_KEY"), 
        base_url="http://18.216.253.243:4000/",
        model="gpt-4o", 
        custom_llm_provider="openai",
        messages=[{"content": enquire, "role": "user"}]
    )
    return response

# Function to load external CSS
def load_css(file_name):
    with open(file_name, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Load CSS from external file
load_css("frontend/styles.css")

# # Add custom HTML for Share button only
# share_button_html = """
# <div style="position: fixed; top: 10px; right: 15px; z-index: 1000;">
#     <button style="
#         background-color: #5c7063; 
#         color: white; 
#         border: none; 
#         border-radius: 5px; 
#         padding: 8px 16px; 
#         font-size: 14px; 
#         cursor: pointer;
#     ">
#         Share
#     </button>
# </div>
# """

# # Render the Share button in Streamlit
# st.markdown(share_button_html, unsafe_allow_html=True)

# Streamlit App Title
st.title("EcoValid")

# Initialize session state for role selection
if "role" not in st.session_state:
    st.session_state.role = "Select an option"

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
        st.rerun()

# Fully use the screen for chat after role selection
#if st.session_state.role != "Select an option":
    #st.subheader(f"Chatting as a {st.session_state.role}")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f"<p style='margin:0; padding:10px;'>{message['content']}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='assistant-message'>{message['content']}</div>", unsafe_allow_html=True)

# React to user input (only available after role selection)
if st.session_state.role != "Select an option":
    if prompt := st.chat_input("Chat with Eco..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(f"<p style='margin:0; padding:10px;'>{prompt}</p>", unsafe_allow_html=True)

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Create a placeholder for assistant response
        response_placeholder = st.empty()

        with st.chat_message("assistant"):
            # Display a spinning loader next to "Thinking..."
            spinner_placeholder = st.markdown("<div class='loader'></div> Generating...", unsafe_allow_html=True)

            # Call the function to get the chatbot result
            result = model_4o(prompt)

            # Remove the spinner after response is received
            spinner_placeholder.empty()

            # Format assistant response
            response = f"Eco: {result['choices'][0]['message']['content']}"

            # Update the placeholder with the actual response
            response_placeholder.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

