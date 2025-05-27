import streamlit as st
import base64
import warnings
import numpy as np
import json
from core.rag_compliance import analyze_compliance, load_documents, retrieve_relevant_docs
import pandas as pd
import re
import requests
import logging
import os
from pathlib import Path







def format_dict(data):
    return [f"Question: {entry['Question']}  Answer: {entry['Answer']}" for entry in data.values()]
    #Question: {entry['Question']}

def format_df(data):
    # Check if the DataFrame has the required columns
    if 'Question' not in data.columns or 'ID' not in data.columns:
        raise ValueError("DataFrame must contain 'Question' and 'ID' columns")
    
    # Convert DataFrame rows to text in the required format
    formatted_data = [
        f"Question: {row['Question']}  ID: {row['ID']}" for _, row in data.iterrows()
    ]
    
    # Return the formatted data as a list of strings
    return formatted_data





def get_summary(content, retries=3):
    prompt = (
        "Analyze the following content and summarize it in a paragraph.\n\n"
        "IMPORTANT: Your summary MUST begin with the risk level ONLY from one of the following:\n"
        "'Unacceptable', 'High', 'Limited', or 'Minimal'.\n"
        "Use this exact format:\n"
        "Unacceptable: <your summary>\n"
        "High: <your summary>\n"
        "Limited: <your summary>\n"
        "Minimal: <your summary>\n\n"
        "In your summary, explicitly mention the specific regulatory provisions or compliance requirements that are not met.\n"
        "Use precise and formal language. Replace vague terms such as 'input' or 'documents' with 'provided system information', 'regulatory provisions', or 'compliance criteria'.\n"
        "Explain clearly the reasons for non-compliance based on the system description or evidence given.\n"
        "If the content is vague, unclear, incomplete, or prevents accurate risk judgment, you MUST select either 'High' or 'Unacceptable'.\n"
        "Do NOT use 'Minimal' or 'Limited' in such cases, even if unsure.\n"
        "DO NOT mention the length or quality of the input text.\n\n"
        f"Content:\n{content}"
    )
    data = {
        "access_id": "trial_version",
        "service_name": "meta_llama70b",
        "query": prompt
    }

    for attempt in range(retries):
        try:
            response = requests.post(
                "https://synchange.com/sync.php",
                headers={"Content-Type": "application/json"},
                data=json.dumps(data),
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("response", "No valid response from API")
            else:
                logging.error(f"API returned status code {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"API call attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                logging.info("Retrying API call...")
    return "Error: API call failed after multiple attempts"


def show_results():
        output = ""
        query = "\n".join(entry.strip() for entry in format_dict(st.session_state.QA))
        if not query:
            return

        # Call RAG Compliance
        try:
            #st.write("Processing...\n")

            # Debug: Ensure the query being sent is correct
            print(f"Query Sent to Backend:\n{query}\n")

            results = analyze_compliance(query, documents_directory="core/documents", top_k=5)

            # Debug: Ensure results are received from the backend
            print(f"Results from Backend:\n{results}\n")

            if not results:
                print("No results returned from the analysis.")
                return

            if "error" in results:
                print(results["error"])
                return

            for doc, res in results.items():
                output += f"Article: {doc}\nResult: {res}\n\n"

            #st.write(output)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        return output



def extract_non_compliant_entries(text_output):
    entries = text_output.lower().strip().split("\n\n")
    data = []
    text_results = ""
    for entry in entries:
        if "does not comply" in entry:
            lines = entry.split("\n")
            try:
                doc_name_line = lines[0]
                doc_name = doc_name_line.split(": ")[1].strip().title().split(".")[0]
            except (IndexError, ValueError):
                continue  # skip this entry if document name is malformed

            reason_match = re.search(r'"reason": "(.*?)"', entry)
            if not reason_match:
                continue  # skip if reason not found

            reason = reason_match.group(1).strip().capitalize()
            compliance = "Does Not Comply"

            text_output = f"Document: {doc_name}\nCompliance: {compliance}\nReason: {reason}"
            text_results += text_output + "\n\n"
            data.append([doc_name, compliance, reason])

    df = pd.DataFrame(data, columns=["Document", "Compliance", "Reason"])
    return df, text_results







def get_next_question_llm(QA, current_question_ID, remaining_questions, documents_directory="C:/Users/moham/OneDrive/Desktop/hack2025/RAGDOLL V1.1/Ragdoll-v1.2/Ragdoll-v1.1/core/documents", top_k=3, retries=3):
    if current_question_ID < 2:
        #get the current anser from the QA dict
        current_answer = QA.get(current_question_ID, {}).get("Answer", "")

        answers_dir = "Answers"
        json_files = [f for f in os.listdir(answers_dir) if f.endswith(".json")]
        filenames_no_ext = [os.path.splitext(f)[0] for f in json_files]

        if current_answer in filenames_no_ext:
            st.session_state.hash = current_answer
            st.session_state.load_answers = True
            st.session_state.start_quiz = False
            st.rerun()

        return current_question_ID + 1, False  # Directly return next question ID for first 5 questions
    

    

    print(" Working Directory:", os.getcwd())
    print(" Absolute Path:", Path(__file__).resolve())
    print("Retrieving docs...")
    
    documents = load_documents(documents_directory)
    if not documents:
        return {"error": "No documents found in the directory."}
    
    QA = "\n".join(entry.strip() for entry in format_dict(QA))
    print("Retrieving relevant docs...")
    print("hi")
    relevant_docs = retrieve_relevant_docs(QA, documents, top_k)
    
    if not relevant_docs:
        return {"error": "No relevant documents found for the query."}
    remaining_questions = "\n".join(entry.strip() for entry in format_df(remaining_questions))
    #st.write(remaining_questions)

    prompt = (
    f"Based on the user's provided answers and the relevant documents, determine the most appropriate remaining question that should be asked next to accurately assess compliance with the relevant documents.\n\n"
    
    f"Current answers:\n{json.dumps(QA, indent=2)}\n\n"
    f"Relevant documents:\n{json.dumps(relevant_docs, indent=2)}\n\n"
    f"Remaining questions:\n{json.dumps(remaining_questions, indent=2)}\n\n"

    f"Return only the next question ID, or the word 'STOP' if you believe no further questions are needed to assess compliance. If 'STOP' is returned, it should indicate that the current answers provide enough information to complete the compliance assessment based on the relevant documents, and the remaining questions will not add more value."
    f"Provide a single integer value or the word 'STOP' as the response nothing more."
    f"Only return an ID between {current_question_ID + 1} and {current_question_ID +10}, inclusive, and ensure it is in the remaining questions."
    )

    data = {
        "access_id": "trial_version",
        "service_name": "meta_llama70b",
        "query": prompt
    }
    #st.write("Retrieving next question...")
    #with st.spinner("Retrieving question..."):

    for attempt in range(retries):
        try:
            response = requests.post(
                "https://synchange.com/sync.php",
                headers={"Content-Type": "application/json"},
                data=json.dumps(data),
                timeout=10
            )
            print("2")
            #st.write("Response received from API")
            #st.write(response.status_code)
            #st.write(response.json())
            if response.status_code == 200:
                #st.write(response.json())
                print(response.json().get("response", "No valid response from API"))
                #also retun a bol false 
                return response.json().get("response", "No valid response from API"), False
            else:
                print("3")
                logging.error(f"API returned status code {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"API call attempt {attempt + 1} failed: {e}")
            print("4")
            if attempt < retries - 1:
                print("5")
                logging.info("Retrying API call...")
    print("Error: API call failed after multiple attempts")
    return "Error: API call failed after multiple attempts"










def save_json():
    with open('Data/answers.json', 'w') as f:
        json.dump(st.session_state.QA, f, indent=4)

def display_risk(risk_level):
    risk_levels= [
    "unacceptable",
    "high",
    "limited",
    "minimal"
    ]
    risk_level= risk_level.lower()
    if risk_level == risk_levels[0]:
        st.error('Unacceptable Risk', icon="❌")
    elif risk_level == risk_levels[1]:
        st.error('High Risk', icon="❌")
    elif risk_level == risk_levels[2]:
        st.warning('Limited Risk', icon="⚠️")
    elif risk_level == risk_levels[3]:
        st.success('Minimal Risk', icon="✅")

    #st.success('Minimal Risk', icon="✅")
    #st.warning('Limited Risk', icon="⚠️")
    #st.error('High Risk', icon="❌")
    
