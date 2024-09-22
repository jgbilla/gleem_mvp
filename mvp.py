# mvp.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set page config for wide layout
st.set_page_config(layout="wide")

# Function to validate email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Function to log email to Google Sheets
def log_email_to_sheet(email):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('./credentials/mvp_tracking.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("User tracking").sheet1  # Adjust the sheet name as needed
    sheet.append_row([email])  # Append the email to the next row

# Page: Email Input
if 'email' not in st.session_state:
    st.session_state.email = ""

st.title("Welcome to Gleem")
email_input = st.text_input("Enter your email to continue:", key='email')

if st.button("Submit Email"):
    if is_valid_email(st.session_state.email):
        log_email_to_sheet(st.session_state.email)
        st.session_state.user_input = ""
        st.session_state.page = "main"  # Proceed to the main app
    else:
        st.error("Please enter a valid email address.")


# Main App: User Input
if 'page' in st.session_state and st.session_state.page == "main":
    st.title("Gleem")
    st.write("What do you want to do with AI?")
    st.text_input("Enter your request:", key='user_input')

    if st.button("Submit"):
        # Simulate model scores
        st.session_state.scores = pd.DataFrame({
            'Model': ['GPT-4o', 'Model B', 'Model C'],
            'Score': [0.8, 0.9, 0.85]
        })
        st.session_state.page = "graph"

# Page 2: Display Graph
if 'page' in st.session_state and st.session_state.page == "graph":
    st.title("Model Scores")

    # Display ranked list of models
    for index, row in st.session_state.scores.iterrows():
        with st.expander(f"{row['Model']} - Score: {row['Score']:.2f}", expanded=False):
            # st.image(f"images/{row['Model'].lower().replace(' ', '_')}.png", caption=row['Model'])  # Adjust image path as needed
            st.write("More information about the selected model goes here.")

#MVP 1: 
#Testing:
# 1. Do people even want to know models that are the best for their task
# 2. Will people actually use those models. 

# Todo: Enter email to use (Check it's an actual email) ✅
    #Also saves the email to a Google Sheets for tracking 

# Todo: Query GPT-4 about capabilities of our models with a score based on the query. #jean - Working on it 
# Todo: Try now button that links you to the model's website. 
# Todo: Add feedback textbox to the bottom of the page. 


#MVP-2
#Todo: Deployment potential cost. 
# Todo: Enter actual question otherwise reject submission 