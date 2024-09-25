# mvp.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import gspread
from openai import OpenAI
from pydantic import BaseModel
import os
import streamlit.components.v1 as components
from datetime import datetime
from google.oauth2.service_account import Credentials
from streamlit.components.v1 import html

if 'openai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

global user_email

# Function to validate email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def log_email_to_sheet(email):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    gsheets_creds = st.secrets["google_sheets"]
    credentials = Credentials.from_service_account_info(gsheets_creds, scopes=scope)
    client = gspread.authorize(credentials)
    sheet = client.open("User tracking").sheet1  # Adjust the sheet name as needed

    # Get all values from the sheet
    all_data = sheet.get_all_values()

    # Check if the email already exists
    for row_index, row in enumerate(all_data):
        if row and row[0] == email:
            # Email found, increment count
            current_count = int(row[1]) if len(row) > 1 and row[1].isdigit() else 0
            new_count = current_count + 1
            sheet.update_cell(row_index + 1, 2, new_count)  # +1 because sheet rows are 1-indexed
            return False, new_count  # Email already existed, return new count

    # If email not found, add new row with email and count 1
    sheet.append_row([email, 1])
    return True, 1  # New email added, count is 1

def get_model_url(model_name):
    urls = {
        'GPT-4o': 'https://chat.openai.com/',
        'Claude 3.5 Sonnet': 'https://www.anthropic.com/claude',
        'o1-preview': 'https://openai.com/',
        'Gemini 1.5 Pro': 'https://gemini.google.com/',
        'Claude 3 Opus': 'https://www.anthropic.com/claude',
        'Claude 3 Sonnet': 'https://www.anthropic.com/claude',
        'Mistral Large 2': 'https://console.mistral.ai/',
        'Llama 3.1 405B Instruct': 'https://ai.meta.com/llama/'
    }
    return urls.get(model_name, '#') 

class Rating(BaseModel):
    score: float
    explanation: str

def get_model_score(model, task):
    response = st.session_state.openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",
            response_format=Rating,
            temperature=0,
            messages=[
                {"role": "system", "content": """You are a helpful assistant that rates the performance of models based on the task they are used for. You will be given a task and a model, and you need to rate the model's performance on the task. You will be given a score and an explanation for the score. Make sure to give a score between 0 and 100, and an explanation of one sentence maximum
                """
                },
                 {"role": "user", "content": f"model: {model}, task: {task}, rating:"}
                
            ]
        )
    out = response.choices[0].message.parsed
    return out

def submit_feedback(email, feedback):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    gsheets_creds = st.secrets["google_sheets"]
    credentials = Credentials.from_service_account_info(gsheets_creds, scopes=scope)
    client = gspread.authorize(credentials)
    
    # Open the Google Sheets document
    sheet = client.open("User tracking")
    
    # Select the "feedback" worksheet, or create it if it doesn't exist
    try:
        feedback_sheet = sheet.worksheet("feedback")
    except gspread.WorksheetNotFound:
        feedback_sheet = sheet.add_worksheet(title="feedback", rows="100", cols="20")
        feedback_sheet.append_row(["Timestamp", "Email", "Feedback"])  # Add headers
    
    # Append the new feedback
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    feedback_sheet.append_row([timestamp, email, feedback])

def track_model_interaction(email):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    gsheets_creds = st.secrets["google_sheets"]
    credentials = Credentials.from_service_account_info(gsheets_creds, scopes=scope)
    client = gspread.authorize(credentials)
    sheet = client.open("User tracking").worksheet("interaction_tracking")  # Use a specific worksheet for interactions

    # Get all values from the sheet
    all_data = sheet.get_all_values()

    # Check if the email already exists
    for row_index, row in enumerate(all_data):
        if row and row[0] == email:
            # Email found, increment count
            current_count = int(row[1]) if len(row) > 1 and row[1].isdigit() else 0
            new_count = current_count + 1
            sheet.update_cell(row_index + 1, 2, new_count)  # +1 because sheet rows are 1-indexed
            return False, new_count  # Email already existed, return new count

    # If email not found, add new row with email and count 1
    sheet.append_row([email, 1])
    return True, 1  # New email added, count is 1
    
def open_page(url):
    open_script= """
        <script type="text/javascript">
            window.open('%s', '_blank').focus();
        </script>
    """ % (url)
    html(open_script)


# Set page config for wide layout
st.set_page_config(layout="wide")

# Initialize session state variables
if 'page' not in st.session_state:
    st.session_state.page = "email_input"
if 'scores' not in st.session_state:
    st.session_state.scores = None
if 'email' not in st.session_state:
    st.session_state.email = ""
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Page: Email Input
if  st.session_state.page == "email_input":
    

    st.title("Welcome to Gleem")
    st.markdown("""
    <h5>Gleem is a tool that helps you find the best AI models for your task.</br>
    You can enter your request and we will rank the models based on their performance.</br>
    You can also submit feedback and we will use it to improve our models.</br></h5>
    """, unsafe_allow_html=True)
    email_info = st.text_input("Enter your email to continue:", value=st.session_state.email)

    if st.button("Submit Email"):
        with st.spinner('Submitting...'):
            if is_valid_email(email_info):
                st.session_state.email = email_info
                log_email_to_sheet(st.session_state.email)
                st.session_state.page = "main"  # Proceed to the main app
            else:
                st.error("Please enter a valid email address.")


# Main App: User Input
if st.session_state.page in ["main", "graph"]:
    st.title("Welcome to Gleem")
    st.markdown("<h3>What do you want to do with AI?</h3>", unsafe_allow_html=True)
    user_input = st.text_input("Enter your request:", key='user_input')

    if st.button("Submit"):
        with st.spinner('Submitting...'):
            # Simulate model scores
            if user_input.strip():
                MODELS = ['GPT-4o', 'Claude 3.5 Sonnet', 'o1-preview', 'Gemini 1.5 Pro', 'Claude 3 Opus', 'Claude 3 Sonnet', 'Mistral Large 2', 'Llama 3.1 405B Instruct']
                task = st.session_state.user_input
                data = {"Score": [], "Explanation": []}
                for model in MODELS:
                    rating = get_model_score(model, task)
                    data['Model'] = MODELS
                    data['Score'].append(rating.score)
                    data['Explanation'].append(rating.explanation)

                st.session_state.scores = pd.DataFrame(data)
                st.session_state.scores = st.session_state.scores.sort_values('Score', ascending=False).reset_index(drop=True)
                st.session_state.page = "graph"
            else:
                st.warning("Please enter a request before submitting.")

# Page 2: Display Graph
    if st.session_state.page == "graph":
        st.title("Model Scores")

        # Display ranked list of models
        for index, row in st.session_state.scores.iterrows():
            expander_label = f"{index + 1}. {row['Model']} - Score: {row['Score']:.2f}"
            with st.expander(expander_label, expanded=True):
                st.markdown(f"""
                <div style="font-size: 24px; font-weight: bold;">
                    {expander_label}
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 18px;'>{row['Explanation']}</p>", unsafe_allow_html=True)
                model_url = get_model_url(row['Model'])
                if st.button(f"Use {row['Model']}"):
                    open_page(model_url)
                    track_model_interaction(st.session_state.email)

        st.markdown("### We'd love to hear your feedback!")
        # Initialize feedback in session state if it doesn't exist
        if 'feedback' not in st.session_state:
            st.session_state.feedback = ""

        feedback = st.text_area("Please share your thoughts or suggestions:", value=st.session_state.feedback, key="feedback_input")
        
        if st.button("Submit Feedback"):
            if feedback.strip():  # Check if feedback is not empty
                submit_feedback(st.session_state.email, feedback)
                st.success("Thank you for your feedback!")
                st.session_state.feedback = ""  # Clear the feedback in session state
            else:
                st.warning("Please enter some feedback before submitting.")

        # Update session state with current feedback
        st.session_state.feedback = feedback

#MVP 1: 
#Testing:
# 1. Do people even want to know models that are the best for their task
# 2. Will people actually use those models. 

# Todo: Enter email to use (Check it's an actual email) ✅
    #Also saves the email to a Google Sheets for tracking 

# Todo: Query GPT-4 about capabilities of our models with a score based on the query. ✅
# Todo: Try now button that links you to the model's website. ✅
# Todo: Add feedback textbox to the bottom of the page. ✅
# Todo: Track how many times a user clicks on a model. ✅


#MVP-2
#Todo: Deployment potential cost. 
# Todo: Enter actual question otherwise reject submission 