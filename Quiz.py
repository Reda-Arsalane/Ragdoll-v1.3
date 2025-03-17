import streamlit as st
import base64
import warnings
import pandas as pd
import numpy as np
from Quiz_utils import *
from Data import *
from report import *


def show_quiz_content(all_questions):
    question_id = st.session_state.current_question
    #print("All Questions DataFrame:")
    #print(all_questions.head())  # Show first few rows
    #print(all_questions['ID'].tolist())
    #print("Current Question ID:", question_id)
        # use last if not found 
    print("length:",len(all_questions))
    filtered_questions = all_questions[all_questions['ID'] == question_id]

    if not filtered_questions.empty:
        question_data = filtered_questions.iloc[0]
    else:
        question_id = all_questions.iloc[-1]['ID']  
        question_data = all_questions.iloc[-1]
    print("Current Question ID:", question_id)
    is_q = False

    if question_data.empty:
        st.write("No question available")
        return
    
    question_text = question_data['Question']
    question_section = question_data['Section']
    question_example = question_data['Example']
    question_info = question_data['Information']
    question_resources = question_data['Resources']

    remaining_questions = all_questions.copy()
    remaining_questions = remaining_questions[~remaining_questions['ID'].isin(all_questions['ID'].tolist()[:st.session_state.current_question])]



    response = st.session_state.responses.get(question_id, "")

    highlighted_text = question_text
    glossary_terms = sorted(terms_definitions.keys(), key=lambda term: len(term), reverse=True)

    for term in glossary_terms:
        if term.lower() in highlighted_text.lower():
            term_start = highlighted_text.lower().find(term.lower())
            termd = highlighted_text[term_start:term_start + len(term)]
            highlighted_text = highlighted_text.replace(termd, f"<span style='color:{st.get_option('theme.primaryColor')}'>{termd}</span>")

    st.markdown(
    f"<h3 style='color: {st.get_option('theme.primaryColor')}; font-weight: bold;'>{question_section}</h3>",
    unsafe_allow_html=True
    )
    st.markdown(f"## {highlighted_text}", unsafe_allow_html=True)

    if question_example:
        st.write(f"{question_example}")

    response = st.text_input("Answer:", value=response, key=f"text_{question_id}")

    progress = (question_id / len(all_questions)) 
    st.progress(progress)

    
    
    if response and st.session_state.found_next_question and st.session_state.current_question != st.session_state.last_question_ID and st.session_state.current_question not in st.session_state.path:
            st.session_state.QA[question_id] = {"Question": question_text, "Answer": response}
            #def get_next_question_llm(QA, current_question_ID, documents_directory="documents", top_k=3, retries=3):
            temp = get_next_question_llm(st.session_state.QA, st.session_state.current_question, remaining_questions)
            #st.write('temp:', temp)

            # Extract the first integer from the response
            #print("temp:",temp)
            match = re.search(r'\d+', str(temp[0]))  # Finds the first sequence of digits
            st.session_state.next_question = int(match.group()) if match else st.session_state.last_question_ID
            if st.session_state.next_question <= st.session_state.current_question:
                st.session_state.next_question = st.session_state.last_question_ID
            st.session_state.stop = temp[1]
            #print("next:",st.session_state.next_question)
            #print("stop:",st.session_state.stop)
            if st.session_state.next_question or st.session_state.stop:
                st.session_state.found_next_question = False

            #print("not found:",st.session_state.found_next_question)
            st.session_state.unable_next = False
            is_q = True
    if st.session_state.stop:
            st.session_state.last_question_ID = st.session_state.next_question
            st.session_state.unable_submit = False
            st.session_state.unable_next = True

    col1, col2, col3 = st.columns([1, 1, 1])


    with col1:
        if st.button("Previous"):
            prev_question_ID = get_previous_question()
            if prev_question_ID:
                st.session_state.current_question = prev_question_ID
                st.rerun()
            else:
                st.warning("No previous question")
            
    with col2:
        # create a dict, key: question_id, value1 = response, value2 = question_text
        if st.button("Next", disabled= False):
                    #print('current ', st.session_state.current_question)
                    #print('next: ', st.session_state.next_question)
                    #print('stop: ', st.session_state.stop)
                    #print("last: ", st.session_state.last_question_ID)
                    if not response or response == "":
                            st.warning("Please provide an answer before proceeding!")
                    elif st.session_state.current_question == st.session_state.last_question_ID:
                        st.warning("This is the last question. Please submit or revise your answers.")
                        st.session_state.unable_submit = False
                    else:   
                            ##print("current:",st.session_state.current_question)
                            ##print("hi2")
                            if st.session_state.current_question not in st.session_state.path:
                                st.session_state.path.append(st.session_state.current_question)
                            #print("history:",st.session_state.history)
                            if st.session_state.current_question in st.session_state.path and st.session_state.path.index(st.session_state.current_question) < len(st.session_state.path)-1:
                                #next question in the history
                                st.session_state.current_question = st.session_state.path[st.session_state.path.index(st.session_state.current_question)+1]
                            else:
                                st.session_state.current_question = st.session_state.next_question
                            ##print("next:",st.session_state.current_question)
                            st.session_state.responses[question_id] = response
                            if question_id not in st.session_state.history:
                                st.session_state.history.append(question_id)
                            st.session_state.expanders_state = {'information': False, 'resources': False, 'glossary': False}
                            st.session_state.unable_next = True
                            st.session_state.found_next_question = True
                            st.rerun()
                        
    with col3:
        if st.button("Submit", disabled= st.session_state.unable_submit):
                if not response:
                    st.warning("Please provide an answer before submitting!")
                else:
                    st.session_state.responses[question_id] = response
                    st.session_state.submitted = True
                    st.rerun()


        

    with st.expander("Information", expanded= True):
        st.write(question_info)

    with st.expander("Resources", expanded=st.session_state.expanders_state['resources']):
        st.write(question_resources)
    return
