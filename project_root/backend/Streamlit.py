import streamlit as st
import os
import requests
from dotenv import load_dotenv
from litellm import completion

#URL to FastAPI server
url = "http://localhost:8000/query"

# Set page title and favicon
st.set_page_config(page_title="EcoValid", page_icon="🌿")  

# Load environment variables from .env file
load_dotenv()

# Function to access the azure api key and get a response from the model
def model_4o(enquire, memory):

    if memory:
        messages = st.session_state.conversation_memory
    else:
        messages = [{"role": "user", "content": enquire}]

    response = completion(
        api_key=os.getenv("API_KEY"),# your api key
        base_url="http://18.216.253.243:4000/",
        model="gpt-4o", #could be changed to any model you want
        custom_llm_provider="openai",
        messages=messages
    )

    return response


def recordInput(userInput):
    # Retrieve stored conversation history
    messages = st.session_state.conversation_memory
    # Append new user message
    messages.append({"role": "user", "content": userInput})


def recordOutput(chatbotOutput):
    # Retrieve stored conversation history
    messages = st.session_state.conversation_memory
    # Append assistant response to history
    messages.append({"role": "assistant", "content": chatbotOutput})
    
    

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
        # Record user input
        recordInput(prompt)
        # Display user message
        with st.chat_message("user"):
            st.markdown(f"<p style='margin:0; padding:10px;'>{prompt}</p>", unsafe_allow_html=True)

        # Generate response using updated function
        with st.chat_message("assistant", avatar="frontend/components/bird.jpg"):
            response_placeholder = st.empty()
            spinner_placeholder = st.markdown("<div class='loader'></div> Generating...", unsafe_allow_html=True)

            # Call function with memory support

            #Check if the prompt is an environmental query.
            instruction = "Does the following prompt ask a technical question about environmental impact data? (Answer with \"yes\" or \"no\".)"
            classification = model_4o(instruction + prompt, False)
            classification_text = classification["choices"][0]["message"]["content"].strip().lower()

            #If it is, route to RAG.
            if classification_text.startswith("yes"):
                #Return the process name and location for each possible answer.
                query_text = prompt + ". Also return the process name and process location of the answer."
                query = {"query": query_text}
                response = requests.post(url, json=query)
                str = response.json()["response"]
                classification = model_4o("Does the location and process name in this question: " + prompt + " Fit with the location and processs name in this answer: " + str + " (Answer with \"yes\" or \"no\".)", False)
                classification_text = classification["choices"][0]["message"]["content"].strip().lower()
                if classification_text.startswith("no"):
                    str = "Sorry! We do not have that data."
                elif st.session_state.role == "Researcher":
                    str = model_4o("Use the following answer to answer a user query but with more context:" + str + " Keep the response under two sentences and data focused.", False)["choices"][0]["message"]["content"]
                elif st.session_state.role == "Policy Maker":
                    str = model_4o("Use the following answer to answer a user query but with more context:" + str + " Keep the response under two sentences. Give an example value to add perspective about the severity of enviornmental impact.", False)["choices"][0]["message"]["content"]
               
                response = f"Eco(RAG): {str}"
                recordOutput(response)
                

                
            #If not, route to GPT.
            else:
                answer = model_4o(prompt, True)
                response = f"Eco(GPT): {answer['choices'][0]['message']['content']}"
                
                recordOutput(answer['choices'][0]['message']['content'])

            print(st.session_state.role)    

            spinner_placeholder.empty()
            response_placeholder.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)