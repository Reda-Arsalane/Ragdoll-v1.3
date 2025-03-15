import streamlit as st
import base64
import warnings
import pandas as pd
import numpy as np
from core.rag_compliance import analyze_compliance 
import os
from Quiz_utils import *
from Home import *
from Quiz import *
from report import *
import re

st.set_page_config(
    layout="wide",
    page_title="RAG DOLL",
    page_icon="assets/iconizer-s.svg",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)



st.markdown("""
<style>
	[data-testid="stHeader"] {
		background-color: transparent;
	}
    [data-testid=stHeaderActionElements]{
        display: none;
    }

</style>""",
unsafe_allow_html=True)

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -3em;
        }

        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.markdown(""" <style>.stDeployButton {display:none;} </style>""", unsafe_allow_html=True)




def main():
    #run comand: streamlit run main.py
    
    st.markdown('<style>' + open(r'style.css').read() + '</style>', unsafe_allow_html=True)

    all_questions = load_questions()
    question_IDs = all_questions['ID'].tolist()
    last_question_ID = question_IDs[-1]
    # copy the all question and remove all question already asked (use st.current_question)

    remaining_questions = all_questions.copy()
    

    

    questions_dict = {
    row['ID']: {
        'Question': row['Question'],
        'Section': row['Section'],
        'Example': row['Example'],
        'Information': row['Information'],
        'Resources': row['Resources']
    }
    for _, row in all_questions.iterrows()
    }

    #print(questions_dict[question_IDs[0]])
    if "QA" not in st.session_state:
        st.session_state.QA = {}
    if 'current_question' not in st.session_state:
        st.session_state.current_question = question_IDs[0]

    if 'responses' not in st.session_state:
        st.session_state.responses = {}

    if 'history' not in st.session_state:
        st.session_state.history = []

    if 'path' not in st.session_state:
        st.session_state.path = []

    if 'show_other' not in st.session_state:
        st.session_state.show_other = False

    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    if 'expanders_state' not in st.session_state:
        st.session_state.expanders_state = {
            'information': True,
            'resources': False,
            'glossary': False
        }
    
    if "start_quiz" not in st.session_state:
        st.session_state.start_quiz = False
    
    if "unable_submit" not in st.session_state:
        st.session_state.unable_submit = True
    
    if "unable_next" not in st.session_state:
        st.session_state.unable_next = True
    
    if "found_next_question" not in st.session_state:
        st.session_state.found_next_question = True
    
    if "next_question" not in st.session_state:
        st.session_state.next_question = st.session_state.current_question

    if "stop" not in st.session_state:
        st.session_state.stop = False

    if "last_question_ID" not in st.session_state:
        st.session_state.last_question_ID = last_question_ID

    if st.session_state.submitted:
        header()
        all_questions = load_questions()
        remaining_questions = all_questions.copy()
        question_IDs = all_questions['ID'].tolist()
        remaining_questions = remaining_questions[~remaining_questions['ID'].isin(question_IDs[:st.session_state.current_question])]
        #st.write(remaining_questions)
        st.markdown(f"""<br/>""", unsafe_allow_html=True)
        st.markdown(
        f"<h3 style='color: {st.get_option('theme.primaryColor')}; font-weight: bold;'> Compliance Analysis and Results: </h3> <br/>",
        unsafe_allow_html=True
        )
        result= show_results()
        clean_result = extract_non_compliant_entries(result)
        summary = get_summary(clean_result[1])
        #risk = first word of summary after removing punctuation and to lower()
        risk = summary.split(" ")[0].lower().strip().replace(":", "")
        st.markdown(f"<h3> Risk Level: {risk.capitalize()} </h3>", unsafe_allow_html=True)

        summary_without_risk = " ".join(summary.split(" ")[1:]) 
        display_risk(risk)
        st.markdown(f"""<br/>""", unsafe_allow_html=True)
        st.markdown(summary_without_risk, unsafe_allow_html=True)
        st.markdown(f"""<br/>""", unsafe_allow_html=True)
        df_s=clean_result[0]
        with st.expander("Non Compliant Entries", expanded=True):
            df_s.set_index("Document", inplace=True)
            st.dataframe(df_s, use_container_width=True)
        st.markdown(f"""<br/>""", unsafe_allow_html=True)
        with st.expander("Summary of Answers", expanded=True):
            df = pd.DataFrame(st.session_state.QA).T
            st.dataframe(df , use_container_width=True)
        save_json()
        return

    image_base64 = get_base64_of_image('assets/iconizer-s.svg')
    #remaining_questions = remaining_questions[~remaining_questions['ID'].isin(question_IDs[:st.session_state.current_question])]
    #query = "\n".join(entry.strip() for entry in format_dict(st.session_state.QA))

    
    if not st.session_state.start_quiz:
        show_home_page()
        col1, col2 = st.columns([1, 1.03])
        with col2:
            if st.button("Start Quiz"):
                st.session_state.start_quiz = True
                st.rerun()
        return
    
    if st.session_state.start_quiz:
        col1, col2 = st.columns([1.6, 1])
        with col1:
            header()
            show_quiz_content(all_questions)

        with col2:
            
            
            #st.write("question_id:",st.session_state.current_question)   
            #remaining_questions = remaining_questions[~remaining_questions['ID'].isin(all_questions['ID'].tolist()[:st.session_state.current_question])]
            #st.write(remaining_questions)
            #st.write("QA: ", st.session_state.QA)
            #st.write("path: ", st.session_state.path)
            #st.write("history: ", st.session_state.history)
            glossary(all_questions)
            #file_uploader()
            return


if __name__ == "__main__":
    #os.system('streamlit run main.py')
    main()