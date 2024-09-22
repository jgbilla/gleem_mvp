# mvp.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set page config for wide layout
st.set_page_config(layout="wide")
# Page 1: User Input
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

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

# Todo: Enter email to use (Check it's an actual email)
# Todo: Enter actual question otherwise reject submission
# Todo: Query GPT-4 about capabilities of our models with a score based on the query. 
# Todo: Try now button that links you to the model's website. 


#Todo: MVP-2: Deployment potential cost. 