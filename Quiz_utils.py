import streamlit as st
import base64
import warnings
import pandas as pd
import numpy as np
import json
from Data import *
import random as ll
from math import ceil

def load_questions():
    df = pd.read_csv("Data/final.csv")
    df.fillna("", inplace=True)
    return df

def get_previous_question():
    if 'history' in st.session_state and st.session_state.history:
        return st.session_state.history.pop()
    return None

def get_next_question(QA, current_question_ID):
    stop = False
    next_question_ID = current_question_ID + 1


    if next_question_ID == 5:
        stop = True
    print("stop:",stop)

    return next_question_ID, stop




def get_n_questions():
    #to do 
    stop = False
    
    #nextQ = ll.randint(question_remaining['ID'].iloc[0], load_questions()['ID'].iloc[0]) - 1
    # nextQ = ll.randint(st.session_state.current_question+1, load_questions()['ID'].iloc[-1]) 
    edge =ceil(((load_questions()['ID'].iloc[-1])+st.session_state.current_question)/2)
    nextQ = ll.randint(st.session_state.current_question, edge) 
    #if last question
    #while nextQ > load_questions()['ID'].iloc[-1]:
        #nextQ = ll.randint(st.session_state.current_question, load_questions()['ID'].iloc[-1] - n + 1)

    # if nextQ == st.session_state.current_question:
    #     nextQ = nextQ + 1
    if nextQ == load_questions()['ID'].iloc[-1]:
        stop = True
        return nextQ ,stop
        
    if nextQ == st.session_state.current_question:
        nextQ = nextQ + 1

    print("next2:",nextQ)
    return nextQ ,stop



def file_uploader():
    uploaded_files = st.file_uploader("Upload relevant System Documentation to provide more context", accept_multiple_files=True)
    if uploaded_files:
        st.success(f"Successfully uploaded {len(uploaded_files)} files.")



def glossary(all_questions):
    with st.expander("Glossary", expanded=True):
                question_id = st.session_state.current_question
                question_data = all_questions[all_questions['ID'] == question_id].iloc[0]

                if question_data.empty:
                    st.write("No question available")
                    return

                glossary_terms = [term for term in terms_definitions if term.lower() in question_data['Question'].lower()]
                
                if glossary_terms:
                    # Find the start index of each term in the text
                    term_positions = []
                    for term in glossary_terms:
                        start_index = all_questions.get(question_data['Question'].lower().find(term.lower()))
                        term_positions.append((start_index, term))
                    # Sort terms
                    term_positions.sort()
                    # Display the terms in the order they appear in the text
                    for _, term in term_positions:
                        st.markdown(f"**<strong><span style='color:{st.get_option('theme.primaryColor')}'>{term}</span>:</strong>** {terms_definitions[term]}", unsafe_allow_html=True)
                else:
                    st.write("No glossary terms found in this question.")

#image_base64 = get_base64_of_image('assets/iconizer-s.svg')

def html_header(image_base64):
    st.markdown(f"""
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Smooch+Sans:wght@100..900&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="style.css">
    </head>
    <div class="header-container">
        <div class="logo-container">
            <img src="data:image/svg+xml;base64,{image_base64}" width="100%">
        </div>
        <div class="title-container">
            <h1>RAG DOLL</h1>
        </div>
    </div>
    <br/>
    <br/>
    <br/>
    <br/>
    """, unsafe_allow_html=True)






