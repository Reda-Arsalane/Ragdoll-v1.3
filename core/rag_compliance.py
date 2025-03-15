import os
import json
import logging
from datetime import datetime
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import base64
import warnings
import pandas as pd
import numpy as np

# Initialize logging
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

# Load documents from the 'documents' directory
def load_documents(directory="documents"):
    docs = {}
    if not os.path.exists(directory):
        logging.warning(f"Documents directory '{directory}' does not exist. Creating the directory.")
        os.makedirs(directory)
        return docs

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read().strip()
                    if content:
                        docs[filename] = content
                    else:
                        logging.warning(f"Skipping empty file: {filename}")
            except UnicodeDecodeError:
                logging.error(f"Encoding issue with file '{filename}'. Attempting recovery.")
                try:
                    with open(filepath, 'r', encoding='latin-1') as file:
                        content = file.read().strip()
                        if content:
                            docs[filename] = content
                except Exception as e:
                    logging.error(f"Failed to recover file '{filename}': {e}")
    return docs

# Find the most relevant documents
def retrieve_relevant_docs(query, documents, top_k=3):
    if not documents:
        logging.warning("No documents available for retrieval.")
        return {}

    doc_names = list(documents.keys())
    doc_contents = list(documents.values())

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(doc_contents + [query])
    similarity_scores = cosine_similarity(vectors[-1], vectors[:-1]).flatten()

    ranked_indices = similarity_scores.argsort()[::-1][:top_k]
    relevant_docs = {doc_names[i]: doc_contents[i] for i in ranked_indices}
    return relevant_docs

# Call the API for a single document
def call_api(query, content, retries=3):
    prompt = (
        f"Analyze the following article and determine whether it complies with the inputs. "
        f"Return 'Complies' or 'Does not comply' with a reason and actionable recommendations to mitigate risks\n\n"
        f'{{ "Article": "Placeholder_Article.txt", "Result": {{ "result": "Complies or Does not comply", "reason": "This is a placeholder response. The actual compliance evaluation will be determined based on the document\'s content." }} }}\n\n'        f"Article: {content}\n\n"
        f"Input: {query}\n\n"
    )
    data = {
        "access_id": "trial_version",
        "service_name": "GWDGChatAI",
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

import streamlit as st

def check_compliance(query, relevant_docs):
    results = {}
    expander_placeholder = st.empty()  # Create a placeholder for the expander
    
    with expander_placeholder.expander("Loading...", expanded=True):
        for doc_name, content in relevant_docs.items():
            st.write(f"Checking compliance for document: {doc_name}")
            analysis = call_api(query, content)
            results[doc_name] = analysis

    expander_placeholder.empty()  # Remove the expander after the loop finishes
    return results


# Main function to analyze compliance
def analyze_compliance(query, documents_directory="documents", top_k=3):
    documents = load_documents(documents_directory)
    if not documents:
        return {"error": "No documents found in the directory."}

    relevant_docs = retrieve_relevant_docs(query, documents, top_k)
    if not relevant_docs:
        return {"error": "No relevant documents found for the query."}

    compliance_results = check_compliance(query, relevant_docs)
    return compliance_results

# Optional CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RAG-based Compliance Analysis")
    parser.add_argument("--query", type=str, required=True, help="Query or report to analyze.")
    parser.add_argument("--documents_dir", type=str, default="documents", help="Directory containing documents.")
    parser.add_argument("--top_k", type=int, default=3, help="Number of relevant documents to analyze.")
    args = parser.parse_args()

    result = analyze_compliance(args.query, args.documents_dir, args.top_k)
    print("\nCompliance Analysis Results:")
    for doc, res in result.items():
        print(f"\nDocument: {doc}\nResult: {res}")



