import streamlit as st
import os
import requests
from dotenv import load_dotenv
from litellm import completion

import re
import io
import base64
import matplotlib.pyplot as plt

# Helper to extract and render LLM-generated Python matplotlib code as an image
def generate_visualization_from_code(code_text):
    """
    Extracts Python code from a markdown code block, executes it,
    and returns a base64-encoded PNG image string of the resulting matplotlib plot.
    """
    # Extract the code block
    match = re.search(r"```python(.*?)```", code_text, re.DOTALL)
    code_snippet = match.group(1).strip() if match else None

    if not code_snippet:
        return None  # No code found

    try:
        # Setup for safe execution
        exec_globals = {"plt": plt}
        exec(code_snippet, exec_globals)

        # Save figure to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)

        # Encode image to base64
        return base64.b64encode(buf.read()).decode("utf-8")

    except Exception as e:
        print("Visualization generation failed:", e)
        return None



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
            temp = 3
    else:
        with st.chat_message("assistant", avatar="frontend/components/bird.jpg"):  # Custom bot icon here
            st.markdown(f"<div class='assistant-message'>Eco: {message['content']}</div>", unsafe_allow_html=True)

# React to user input (only after role selection)
if st.session_state.role != "Select an option":
    thinkTrej = "<br><br><b>Thinking Trajectory</b><br>"
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

            # Check if the prompt is an environmental query
            instruction = "Does the following prompt ask a technical question about environmental impact data? (Answer with \"yes\" or \"no\".)"
            formatted_prompt = f"\n\t\t- {prompt}"
            classification = model_4o(f"{instruction}{formatted_prompt}", False)
            classification_text = classification["choices"][0]["message"]["content"].strip().lower()

            # Update Thinking Trajectory
            thinkTrej = f"<br><br><b>Thinking Trajectory</b><br>"
            thinkTrej += f"<br><b>LLM input:</b> {instruction}<br>{formatted_prompt}<br>"
            thinkTrej += f"<b><br>LLM response:</b> {classification_text}<br>"

            # If it is, route to RAG
            if classification_text.startswith("yes"):
                query_text = prompt + " Also return the process name and process location of the answer."
                thinkTrej += f"<br><br><b>RAG input:</b> {query_text}"
                query = {"query": query_text}
                response = requests.post(url, json=query)
                str_response = response.json()["response"]
                thinkTrej += f"<br><br><b>RAG output:</b> {str_response}"
                
                classification = model_4o(
                    f"Does the location and process name in this question: {prompt} fit with the location and process name in this answer: {str_response} (Answer with \"yes\" or \"no\".)",
                    False,
                )
                thinkTrej += f"<br><br><b>LLM input:</b> Does the location and process name in this question: {prompt} fit with the location and process name in this answer: {str_response} (Answer with \"yes\" or \"no\".)"
                classification_text = classification["choices"][0]["message"]["content"].strip().lower()
                thinkTrej += f"<br><br><b>LLM output:</b> {classification_text}"
                
                if classification_text.startswith("no"):
                    str_response = "Sorry! We do not have that data."
                elif st.session_state.role == "Researcher":
                    str_response = model_4o(
                        f"Respond using the information in the following answer: {str_response} Keep the response under two sentences and data focused.",
                        False,
                    )["choices"][0]["message"]["content"]
                    thinkTrej += f"<br><br><b>LLM input:</b> Respond using the information in the following answer: {str_response} Keep the response under two sentences and data focused."
                    thinkTrej += f"<br><br><b>LLM output:</b> {str_response}"
                elif st.session_state.role == "Policy Maker":
                    str_response = model_4o(
                        f"Respond using the information in the following answer: {str_response} Keep the response under two sentences. Give an example value to add perspective about the severity of environmental impact.",
                        False,
                    )["choices"][0]["message"]["content"]
                    thinkTrej += f"<br><br><b>LLM input:</b> Respond using the information in the following answer: {str_response} Keep the response under two sentences. Give an example value to add perspective about the severity of environmental impact."
                    thinkTrej += f"<br><br><b>LLM output:</b> {str_response}"


                viz_check_prompt = (
                "Given the following answer, determine whether a chart/visualization would meaningfully improve user understanding. "
                "Only respond with 'yes' if the answer contains at least 2 or more values or comparisons that could be shown visually. "
                "Respond with 'no' if the answer is just a single fact, statistic, or statement.\n\n"
                f"Answer: {str_response}"
)
                viz_check = model_4o(viz_check_prompt, False)
                viz_check_text = viz_check["choices"][0]["message"]["content"].strip().lower()

                if viz_check_text.startswith("yes"):
                    # Ask LLM to generate visualization code
                    viz_prompt = (
                    f"Given the following question and answer, return Python code using ONLY matplotlib "
                    f"to generate a simple visualization to support the answer. "
                    f"Use plt.subplots(), and ensure the chart includes a title and axis labels. "
                    f"Return ONLY the code in a Python code block, and DO NOT include explanations or markdown. "
                    f"And please double check the code to make sure there are no erros. This code is going to be ran automatically. \n\n"
                    f"Question: {prompt}\nAnswer: {str_response}"
)
                    viz_response = model_4o(viz_prompt, False)
                    code_text = viz_response["choices"][0]["message"]["content"]

                    viz_img = generate_visualization_from_code(code_text)
                    # Add image to response
                    if viz_img:
                        str_response += f'<br><br><b>Visualization:</b><br><img src="data:image/png;base64,{viz_img}" width="600"/>'
                    else:
                        str_response += f'<br><br><b>Visualization:</b> <i>(Could not generate visualization)</i>'
                else:
                    str_response += f'<br><br><b>Visualization:</b> <i>(Not needed for this answer)</i>'
               
                response = f"<b>Eco(RAG):</b> {str_response + thinkTrej}"
                recordOutput(response)

            # If not, route to GPT
            else:
                thinkTrej += f"<br><b>LLM input:</b> {prompt}"
                answer = model_4o(prompt, True)
                str_response = answer['choices'][0]['message']['content']
                thinkTrej += f"<br><br><b>LLM output:</b> {str_response}"


                response = f"<b>Eco(GPT):</b> {str_response + thinkTrej}"
                recordOutput(response)
   
            spinner_placeholder.empty()
            response_placeholder.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)
