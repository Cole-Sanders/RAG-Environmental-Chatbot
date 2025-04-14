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

def checkForLocation(query):
    instruction = "Does this query specify a single region? Answer \"yes\" or \"no\". \nQuery:"
    query_text = instruction + query
    response = model_4o(query_text, False)["choices"][0]["message"]["content"]
    if "yes" in response.lower():
        return True
    else:
        return False


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
            temp = 3
    else:
        with st.chat_message("assistant", avatar="frontend/components/bird.jpg"):  # Custom bot icon here
            st.markdown(f"<div class='assistant-message'>Eco: {message['content']}</div>", unsafe_allow_html=True)

# React to user input (only after role selection)
if st.session_state.role != "Select an option":
    thinkTrej = "<br><br>Thinking Trejectory:<br>"
    if prompt := st.chat_input("Chat with Eco..."):
        # Record user input
        recordInput(prompt)
        # Display user message
        with st.chat_message("user"):
            st.markdown(f"<p style='margin:0; padding:10px;'>{prompt}</p>", unsafe_allow_html=True)
            # st.markdown(f"<p style='margin:0; padding:10px;'>abcdefg</p>", unsafe_allow_html=True)

        # Generate response using updated function
        with st.chat_message("assistant", avatar="frontend/components/bird.jpg"):
            response_placeholder = st.empty()
            spinner_placeholder = st.markdown("<div class='loader'></div> Generating...", unsafe_allow_html=True)

            

            #Check if the prompt is an environmental query.
            instruction = "Based on the following input, classify the user's intent as one of the following categories: \n\"query\"" \
                "if the user is asking a technical question about environmental impact data. \n\"validate\" if the user is requesting" \
                "validation of environmental impact data they have provided.\n\"neither\" if the input does not fit into either category." \
                "Provide only the category name as the answer. Provide the correct answer for each location.\nInput:" 
            classification = model_4o(instruction + prompt, False)
            classification_text = classification["choices"][0]["message"]["content"].strip().lower()
            thinkTrej = thinkTrej + "LLM input: " + instruction + prompt + "<br>" + "LLM response: " + classification_text
            #If it is, route the query to RAG.
            if classification_text.startswith("query"):

                #Check if the query specifies a single location.
                if (checkForLocation(prompt)):
                    query_text = prompt + ". Also return the process name."
                    thinkTrej = thinkTrej + "<br>RAG input: " + query_text
                    query = {"query": query_text}
                    response = requests.post(url, json=query)
                    str = response.json()["response"]
                    thinkTrej = thinkTrej + "<br>RAG output:" + str
                    
                #If it does not, find the answers for every location.
                else:
                    #Return the process name of the answer.
                    instruction =  "Provide just the name of the process relevant to my query. \nQuery:"
                    query_text = instruction + prompt
                    thinkTrej = thinkTrej + "<br>RAG input: " + query_text 
                    query = {"query": query_text}
                    response = requests.post(url, json=query)
                    processName = response.json()["response"]
                    thinkTrej = thinkTrej + "<br>RAG output:" + processName

                    #Find all of the locations.
                    instruction =  "Provide all the locations relvent to this process name." \
                        + "List them in the format \"Location1,Location2,etc.\" Process Name: "
                    query_text = instruction + processName
                    thinkTrej = thinkTrej + "<br>RAG input: " + query_text 
                    query = {"query": query_text}
                    response = requests.post(url, json=query)
                    locations = response.json()["response"]
                    thinkTrej = thinkTrej + "<br>RAG output:" + locations
                    
                    locations = locations.split(",")
                    
                    str = ""


                    for location in locations:
                        query_text = "Answer this query: " + prompt + " Using the location: " + location + " and the process name: " + processName + ".\n"
                        thinkTrej = thinkTrej + "<br>RAG input: " + query_text 
                        query = {"query": query_text}
                        response = requests.post(url, json=query)
                        answer = response.json()["response"]
                        thinkTrej = thinkTrej + "<br>RAG output:" + answer
                        str = str + answer + "\n"
                    
                if st.session_state.role == "Researcher":
                    researcher_instruction = "You are answering a question about environmental impact using real data. \nUse the retrieved information below to craft your response, ensuring accuracy.\nRetrieved Data: " \
                        + str + "User query:" + prompt + "\n" + "Answer the user query factually without making assumptions. Craft your answer to a researcher audience."
                    str = model_4o(researcher_instruction, False)["choices"][0]["message"]["content"]
                    thinkTrej = thinkTrej + "<br>LLM input: " + researcher_instruction
                    thinkTrej = thinkTrej + "<br>LLM output: " + str

                elif st.session_state.role == "Policy Maker":
                    policy_instruction = "You are answering a question about environmental impact using real data. \n"\
                            + "Use the retrieved information below to craft your response, ensuring accuracy.\nRetrieved Data: " \
                            + str + "User query:" + prompt + "\n" + "Answer the user query factually without making assumptions." \
                            + " Craft your answer to a policy maker audience."
                    str = model_4o(policy_instruction, False)["choices"][0]["message"]["content"]
                    thinkTrej = thinkTrej + "<br>LLM input: " + policy_instruction
                    thinkTrej = thinkTrej + "<br>LLM output: " + str
                
                response = f"Eco(RAG): {str + thinkTrej}"
                #response = f"Eco(RAG): {str}"
                    
                recordOutput(response)
                
            #If it is a validation question, route to RAG
            elif classification_text.startswith("validate"):
                thinkTrej = thinkTrej + "<br>LLM input: " + "Does this query specify a single location? Answer \"yes\" or \"no\". \nQuery:"
                hasLocation = checkForLocation(prompt)
                thinkTrej = thinkTrej + "<br>LLM output: " + str(hasLocation)
                if hasLocation:
                    query_text = "Answer this query: " + prompt + ".\nIf the data is incorrect, provide the correct data."
                    thinkTrej = thinkTrej + "<br>RAG input: " + query_text
                    query = {"query": query_text}
                    response = requests.post(url, json=query)
                    str = response.json()["response"]
                    
                    thinkTrej = thinkTrej + "<br>RAG output:" + str
                
                else:

                    str = "Please provide a single location to validate the data."
                    
                response = f"Eco(RAG): {str}"
                recordOutput(response)
                
            #If not, route to GPT.
            else:

                thinkTrej = thinkTrej + "<br>LLM input: " + prompt
                answer = model_4o(prompt, True)
                response = f"Eco(GPT): {answer['choices'][0]['message']['content'] + thinkTrej}"
                thinkTrej = thinkTrej + "<br>LLM output: " + answer['choices'][0]['message']['content']
                recordOutput(answer['choices'][0]['message']['content'])
   
            thinkTrej = ""
            spinner_placeholder.empty()
            response_placeholder.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)