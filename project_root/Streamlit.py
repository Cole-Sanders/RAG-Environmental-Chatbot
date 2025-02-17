import streamlit as st
import os
from dotenv import load_dotenv
from litellm import completion

# Function to access the azure api key and get a response from the model
def model_4o(enquire):
    response = completion(
        api_key=os.getenv("API_KEY"),# your api key
        base_url="http://18.216.253.243:4000/",
        model="gpt-4o", #could be changed to any model you want
        custom_llm_provider="openai",
        messages=[{"content": enquire, "role": "user"}]
    )
    return response

# Load environment variables from .env file
load_dotenv()

# Function to load CSS from external file
def load_css(file_name):
    with open(file_name, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# Load external CSS
load_css("frontend/pages/styles.css")

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

    # Call the function to get the chatbot result 
    result = model_4o(prompt)

    # Make an API request using the API key (Example usage)
    response = f"Eco: {result['choices'][0]['message']['content']}"  # Placeholder response

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})