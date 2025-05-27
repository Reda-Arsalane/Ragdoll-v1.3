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
import json
import hashlib


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

    if "load_answers" not in st.session_state:
        st.session_state.load_answers = False
    
    if "hash" not in st.session_state:
        st.session_state.hash = None

    if "show_home" not in st.session_state:
        st.session_state.show_home = True
    
    if "report_generated" not in st.session_state:
        st.session_state.report_generated = False
    
    if "reset_quiz" not in st.session_state:
        st.session_state.reset_quiz = False

    if "modified" not in st.session_state:
        st.session_state.modified = False

    if "submission_report" not in st.session_state:
        st.session_state.submission_report = {}
    


    def quiz_all():    
        col1, col2 = st.columns([1.6, 1])
        with col1:
            header()
            show_quiz_content(all_questions)

        with col2:
            
            if st.button("Restart Quiz"):
                st.session_state.reset_quiz = True
                reset_quiz_state()
                st.rerun()
                return

            #st.write("modified:", st.session_state.modified)
            #st.write("questionsss_id:",st.session_state.current_question)   
            #remaining_questions = remaining_questions[~remaining_questions['ID'].isin(all_questions['ID'].tolist()[:st.session_state.current_question])]
            #st.write(remaining_questions)
            #st.write("responses: ", st.session_state.responses)
            #st.write("QA: ", st.session_state.QA)
            #st.write("path: ", st.session_state.path)
            #st.write("history: ", st.session_state.history)
            glossary(all_questions)
            #file_uploader()
            return

    def reset_quiz_state():
        st.session_state.QA = {}
        st.session_state.current_question = question_IDs[0]
        st.session_state.responses = {}
        st.session_state.history = []
        st.session_state.path = []
        st.session_state.show_other = False
        st.session_state.submitted = False
        st.session_state.expanders_state = {
            'information': True,
            'resources': False,
            'glossary': False
        }
        st.session_state.start_quiz = True  # resume quiz
        st.session_state.unable_submit = True
        st.session_state.unable_next = True
        st.session_state.found_next_question = True
        st.session_state.next_question = question_IDs[0]
        st.session_state.stop = False
        st.session_state.last_question_ID = question_IDs[-1]
        st.session_state.load_answers = False
        st.session_state.hash = None
        st.session_state.show_home = False
        st.session_state.report_generated = False
        st.session_state.modified = False
        st.session_state.submission_report = {}


    def render_submission_output(report):
        header()
        all_questions = load_questions()
        question_IDs = all_questions['ID'].tolist()

        
        summary = report["summary"]
        risk = report["risk_level"]
        result = report["compliance_details"]

        st.markdown(
            f"<h3 style='color: {st.get_option('theme.primaryColor')}; font-weight: bold;'> Compliance Analysis and Results: </h3> <br/>",
            unsafe_allow_html=True
        )
        st.markdown(f"<h3> Risk Level: {risk.capitalize()} </h3>", unsafe_allow_html=True)

        summary_without_risk = " ".join(summary.split(" ")[1:])

        col1, col2 = st.columns([0.5, 1.5])
        with col1:
            display_risk(risk)
        
        with col2:
            if st.button("Go Back to Quiz"):
                #st.session_state.current_question = st.session_state.current_question or question_IDs[0]
                st.session_state.submitted = False
                #st.session_state.show_home = False
                st.session_state.report_generated = True
                st.session_state.start_quiz = True
                st.rerun()
                return



        st.markdown(f"""<br/>""", unsafe_allow_html=True)
        st.markdown(summary_without_risk, unsafe_allow_html=True)
        st.markdown(f"""<br/>""", unsafe_allow_html=True)

        clean_result = extract_non_compliant_entries(result)
        df_s = clean_result[0]
        with st.expander("Non Compliant Entries", expanded=True):
            df_s.set_index("Document", inplace=True)
            st.dataframe(df_s, use_container_width=True)

        st.markdown(f"""<br/>""", unsafe_allow_html=True)
        with st.expander("Summary of Answers", expanded=True):
            df = pd.DataFrame(report["answers"]).T
            st.dataframe(df, use_container_width=True)

    # Submitted case
    if st.session_state.submitted:
        if not st.session_state.report_generated:
            if not st.session_state.modified and st.session_state.submission_report != {}:
                render_submission_output(st.session_state.submission_report)
            else:	
                result = show_results()
                clean_result = extract_non_compliant_entries(result)
                summary = get_summary(clean_result[1])
                risk = summary.split(" ")[0].lower().strip().replace(":", "")
                
                submission_report = {
                    "answers": st.session_state.QA,
                    "summary": summary,
                    "risk_level": risk,
                    "compliance_details": result
                }

                report_json = json.dumps(submission_report, indent=4)
                report_hash = hashlib.sha256(report_json.encode('utf-8')).hexdigest()
                output_path = f"Answers/{report_hash}.json"

                with open(output_path, "w") as f:
                    f.write(report_json)

                st.session_state.hash = report_hash
                render_submission_output(submission_report)
                save_json()
                st.session_state.report_generated = True
                st.session_state.submission_report = submission_report
                st.session_state.modified = False

                return
        else:
            quiz_all()

    # Load answers case
    if st.session_state.load_answers and st.session_state.hash:
        if not st.session_state.report_generated:
            path = f"Answers/{st.session_state.hash}.json"
            if os.path.exists(path):
                with open(path, "r") as f:
                    loaded_report = json.load(f)
                render_submission_output(loaded_report)
                st.session_state.report_generated = True
            else:
                st.error("Saved answers not found for the given hash.")
        else:
            quiz_all()


    image_base64 = get_base64_of_image('assets/iconizer-s.svg')
        #remaining_questions = remaining_questions[~remaining_questions['ID'].isin(question_IDs[:st.session_state.current_question])]
        #query = "\n".join(entry.strip() for entry in format_dict(st.session_state.QA))

    
    if st.session_state.show_home:
        show_home_page()
        col1, col2 = st.columns([1, 1.03])
        with col2:
            if st.button("Start Quiz"):
                st.session_state.show_home = False
                st.session_state.start_quiz = True
                st.rerun()
        return
    
    



    if st.session_state.start_quiz:
        quiz_all()

    


if __name__ == "__main__":
    #os.system('streamlit run main.py')
    main()