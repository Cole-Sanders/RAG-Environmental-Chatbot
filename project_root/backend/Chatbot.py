import streamlit as st
import os
import requests
from dotenv import load_dotenv
from litellm import completion

import re
import io
import base64
import matplotlib.pyplot as plt

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter

def export_as_pdf(conversation_memory):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    styles.add(ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold'))
    custom_italic = ParagraphStyle('CustomItalic', parent=styles['Normal'], fontName='Helvetica-Oblique')
    styles.add(custom_italic)
    
    story = []

    # Add user role at the top of the PDF
    role_paragraph = Paragraph(f"<b>Role:</b> {st.session_state.role}", styles['Bold'])
    story.append(role_paragraph)
    story.append(Spacer(1, 12))

    for msg in conversation_memory:
        if msg['role'] == 'user':
            story.append(Paragraph(f"<b>User:</b>", styles['Bold']))
            story.append(Paragraph(msg['content'], styles['Normal']))
            story.append(Spacer(1, 12))
        elif msg['role'] == 'assistant':
            story.append(Paragraph(f"<b>Assistant:</b>", styles['Bold']))
            content = msg['content']
            content = content.replace('**Eco(RAG):**', '<b>Eco(RAG):</b>')
            content = content.replace('**Eco(GPT):**', '<b>Eco(GPT):</b>')
            content = content.replace('**Process details:**', '<b>Process details:</b>')
            content = content.replace('**Process Name:**', '<b>Process Name:</b>')
            content = content.replace('**Location:**', '<b>Location:</b>')
            content = content.replace('**Reasoning:**', '<b>Reasoning:</b>')
            paragraphs = content.split('\n\n')
            for p in paragraphs:
                story.append(Paragraph(p, styles['Normal']))
                story.append(Spacer(1, 6))
            story.append(Spacer(1, 12))

    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

def render_homepage():
    st.title("🌿 Welcome to EcoValid")
    st.markdown("""
    <style>
    .intro-title { font-size: 1.5em; font-weight: bold; color: #2E7D32; }
    .tip {
        background-color: #1e1e1e;  /* darker bg for dark mode */
        color: #d9ffd9;             /* light green text */
        border-left: 5px solid #2E7D32;
        padding: 10px;
        margin-top: 10px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="intro-title">Your AI-powered assistant for understanding environmental impact data.</div>

    ### 🧭 What is EcoValid?
    EcoValid helps **researchers** and **policy makers** explore complex environmental data using simple questions.

    ### 🛠 Why use it?
    - ✅ No need to dig through dense reports  
    - ✅ Fast, **data-backed** answers  
    - ✅ Tailored results for your role  
    - ✅ Helpful visualizations

    ### 💬 Try asking:
    - *“What is the acidification impact of coal electricity in Ohio?”*  
    - *“How does wind energy compare to natural gas for global warming?”*

    <div class="tip">
    💡 **Tips**:  
    • Be specific (e.g., include a location or process)  
    • Use the role selector once you start  
    </div>
    """, unsafe_allow_html=True)

    if st.button("👉 Start Chatting with Eco"):
        st.session_state.page = "chat"
        st.rerun()

if "page" not in st.session_state:
    st.session_state.page = "home"



#URLs to FastAPI server
name_url = "http://localhost:8000/namequery"
location_url = "http://localhost:8000/locationquery"

if st.session_state.page == "home":
    render_homepage()
elif st.session_state.page == "chat":

    # Set page title and favicon
    st.set_page_config(page_title="EcoValid", page_icon="🌿")  

    # Load environment variables from .env file
    load_dotenv()

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
        instruction = "Does this query specify a single region? (Global counts as a region) Answer \"yes\" or \"no\". \nQuery:"
        query_text = instruction + query
        response = model_4o(query_text, False)["choices"][0]["message"]["content"]
        if "yes" in response.lower():
            return True
        else:
            return False

    # Return the data associated with a process based on its name and location.
    def pullProcessData(processName, processLocation):
        processName = processName.strip().rstrip(".")
        processLocation = processLocation.strip().rstrip(".")
        with open("backend/TextData.txt", "r") as file:
            for line in file:
                dataNode = line.strip()
                location = dataNode.split(".")[2].strip()
                if (processName in dataNode) and (processLocation == location):
                    return dataNode
        return ""

    def getProcesses(prompt):
        # Return the top 10 processes that match the query by name.
        query = {"query": query_text}
        response = requests.post(name_url, json=query)
        str = response.json()["response"]
        return str

    def getLocations(prompt):
        # Return the locations for each instance of the process.
        query = {"query": query_text}
        response = requests.post(location_url, json=query)
        str = response.json()["response"]
        return str


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
        
        if st.button("EXPORT CHAT"):
            pdf = export_as_pdf(st.session_state.conversation_memory)
            st.download_button(
                label="Download PDF",
                data=pdf,
                file_name="chat_export.pdf",
                mime="application/pdf"
    )
        


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

                    viz_possible = False

                    #Check if the query specifies a single location.
                    if (checkForLocation(prompt)):
                        # Return the top 10 processes that match the query by name and location.
                        query_text = prompt
                        str = getProcesses(query_text)
                        thinkTrej = thinkTrej + "<br>RAG input: " + query_text + "<br>RAG output: " + str

                        # Send all 10 processes to the LLM and ask it to find the best match for the query based on name and location.
                        instruction = "Given this query, return just the verbatium text (process name and location) of the process that best matches the query. \nQuery:" + prompt + "\n" + str
                        str = model_4o(instruction, False)["choices"][0]["message"]["content"]
                        thinkTrej = thinkTrej + "<br>LLM input: " + instruction + "<br>LLM output: " + str
                        nameAndLoc = str.split(".")

                        # Return the process data for the best match.
                        str = pullProcessData(nameAndLoc[0], nameAndLoc[1])
                        thinkTrej = thinkTrej + "<br>Matched Process Data:" + str
                        
                    

                    #If it does not specify a location, find the answers for every location in the dataset.
                    else:
                        viz_possible = True
                        # Return the top 10 processes that match the query by name.
                        query_text = prompt
                        str = getProcesses(query_text)
                        thinkTrej = thinkTrej + "<br>RAG input: " + query_text + "<br>RAG output: " + str

                        # Send all 10 processes to the LLM and ask it to find the best match for the query based on name alone.
                        instruction = "Given this query, return just the verbatium text of the process that best matches the query, minus its location. \nQuery:" + prompt + "\n" + str
                        processName = model_4o(instruction, False)["choices"][0]["message"]["content"]
                        thinkTrej = thinkTrej + "<br>LLM input: " + instruction + "<br>LLM output: " + str

                        #Find all of the locations for which there is data for the chosen process.
                        instruction =  "Provide all the locations for each instance of the following process." \
                            + "List them in the format \"Location1,Location2,etc.\" Process Name: "
                        query_text = instruction + str
                        locations = getLocations(query_text) 
                        thinkTrej = thinkTrej + "<br>RAG input: " + query_text + "<br>RAG output:" + locations
                        locations = locations.split(",")

                        # For each location, pull the process data and add it to the response.
                        for location in locations:
                            answer = pullProcessData(processName, "Location: " + location + ".")
                            thinkTrej = thinkTrej + "<br>Matched Process Data:" + answer
                            str = str + answer + "\n"
                        
                        
                    
                    # Send the process data to the LLM and ask it to answer the user query as a researcher.
                    if st.session_state.role == "Researcher":
                        researcher_instruction = "You are answering a question about environmental impact using real data. Use this process data to answer the user query. \nRetrieved Data: " \
                            + str + "User query:" + prompt + "\n" + "Answer the user query factually without making assumptions. Craft your answer to a researcher audience. Do not show equaitons." \
                            + " Show the process name and location in your answer."
                        str = model_4o(researcher_instruction, False)["choices"][0]["message"]["content"]
                        thinkTrej = thinkTrej + "<br>LLM input: " + researcher_instruction + "<br>LLM output: " + str

                    # Send the process data to the LLM and ask it to answer the user query as a policy maker.
                    elif st.session_state.role == "Policy Maker":
                        policy_instruction = "You are answering a question about environmental impact using real data. \n"\
                                + "Use the retrieved information below to craft your response, ensuring accuracy.\nRetrieved Data: " \
                                + str + "User query:" + prompt + "\n" + "Answer the user query factually without making assumptions." \
                                + " Craft your answer to a policy maker audience and explain all technical terms and units. Do not show equations." \
                                + " Show the process name and location in your answer."
                        str = model_4o(policy_instruction, False)["choices"][0]["message"]["content"]
                        thinkTrej = thinkTrej + "<br>LLM input: " + policy_instruction + "<br>LLM output: " + str
                    

                    if viz_possible:
                        # Ask LLM to generate visualization code
                        viz_prompt = (
                        f"Given the following question and answer, return Python code using ONLY matplotlib "
                        f"to generate a simple visualization to support the answer. "
                        f"Use plt.subplots(), and ensure the chart includes a title and axis labels. "
                        f"Return ONLY the code in a Python code block, and DO NOT include explanations or markdown. "
                        f"And please double check the code to make sure there are no erros. This code is going to be ran automatically. \n\n"
                        f"Question: {prompt}\nAnswer: {str}"
    )
                        viz_response = model_4o(viz_prompt, False)
                        code_text = viz_response["choices"][0]["message"]["content"]

                        viz_img = generate_visualization_from_code(code_text)
                        # Add image to response
                        if viz_img:
                            str += f'<br><br><b>Visualization:</b><br><img src="data:image/png;base64,{viz_img}" width="600"/>'


                    response = f"Eco(RAG): {str + thinkTrej}"
                    #response = f"Eco(RAG): {str}"
                        
                    recordOutput(response)
                    
                #If it is a validation question, route to RAG
                elif classification_text.startswith("validate"):
                    
                    #Check if the query specifies a single location.
                    hasLocation = checkForLocation(prompt)

                    #If it does, continue. 
                    if hasLocation:
                        # Return the top 10 processes that match the query by name and location.
                        query_text = prompt
                        str = getProcesses(query_text)
                        thinkTrej = thinkTrej + "<br>RAG input: " + query_text + "<br>RAG output: " + str

                        # Send all 10 processes to the LLM and ask it to find the best match for the query based on name and location.
                        instruction = "Given this query, return just the verbatium text of the process (process name and location) that best matches the query. \nQuery:" + prompt + "\n" + str
                        str = model_4o(instruction, False)["choices"][0]["message"]["content"]
                        thinkTrej = thinkTrej + "<br>LLM input: " + instruction + "<br>LLM output: " + str
                        nameAndLoc = str.split(".")

                        # Return the process data for the best match.
                        str = pullProcessData(nameAndLoc[0], nameAndLoc[1])
                        thinkTrej = thinkTrej + "<br>Matched Process Data:" + str

                        # Send the process data to the LLM and ask it to validate the user data for a researcher audience.
                        if st.session_state.role == "Researcher":
                            researcher_instruction = "You are validating user data about environmental impact using real data. Use this process data to check the accuracy of the user data. \nRetrieved Data: " \
                                + str + "User data:" + prompt + "\n" + "Validate user data factually without making assumptions. Craft your answer to a researcher audience. Do not use Equations." \
                                + " List the process name and location in after the answer."
                            str = model_4o(researcher_instruction, False)["choices"][0]["message"]["content"]
                            thinkTrej = thinkTrej + "<br>LLM input: " + researcher_instruction + "<br>LLM output: " + str

                        # Send the process data to the LLM and ask it to validate the user data for a policy maker audience.
                        elif st.session_state.role == "Policy Maker":
                            policy_instruction = "You are validating user data about environmental impact using real data. Use this process data to check the accuracy of the user data. \nRetrieved Data: " \
                                + str + "User data:" + prompt + "\n" + "Validate user data factually without making assumptions. Craft your answer to a policy maker audience and give an example for comparison. Do not use Equations." \
                                + " List the process name and location in after the answer."
                            str = model_4o(policy_instruction, False)["choices"][0]["message"]["content"]
                            thinkTrej = thinkTrej + "<br>LLM input: " + policy_instruction + "<br>LLM output: " + str
                    
                    # If it does not specify a location, ask the user to specify one.
                    else:
                        str = "It looks like you asked a validation question. Answers vary based on location. Please ask your question again with a location specified."
                        
                    response = f"Eco(RAG): {str + thinkTrej}"
                    recordOutput(response)
                    
                #If not a enviornmental impact question, route to GPT.
                else:
                    answer = model_4o(prompt, True)
                    response = f"Eco(GPT): {answer['choices'][0]['message']['content']}"
                    thinkTrej = thinkTrej + "<br>LLM input: " + prompt + "<br>LLM output: " + answer['choices'][0]['message']['content']
                    recordOutput(answer['choices'][0]['message']['content'])
    
                thinkTrej = ""
                spinner_placeholder.empty()
                response_placeholder.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)