import os
import json
import logging
from datetime import datetime
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
    try:
        docs = {}
        print(directory)
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
                        if content:  # Skip empty files
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
                            else:
                                logging.warning(f"Skipping empty file after recovery attempt: {filename}")
                    except Exception as e:
                        logging.error(f"Failed to recover file '{filename}': {e}")
                except Exception as e:
                    logging.error(f"Error reading file '{filename}': {e}")

        if not docs:
            logging.warning(f"No valid text files found in directory '{directory}'.")
        return docs
    except Exception as e:
        logging.critical(f"Failed to load documents: {e}")
        return {}

# Call the API for a single document
def call_api(query, content, retries=3):
    try:
        prompt = (
            f"Analyze the following content and determine whether it complies with the query. "
            f"Return 'Complies' or 'Does not comply' with a reason.\n\n"
            f"Content: {content}\n\n"
            f"Query: {query}\n\nAnswer:"
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
    except Exception as e:
        logging.critical(f"Unexpected error in API call: {e}")
        return "Error: API call failed"

# Check compliance for all relevant documents
def check_compliance(query, relevant_docs):
    results = {}
    for doc_name, content in relevant_docs.items():
        logging.info(f"Checking compliance for document: {doc_name}")
        analysis = call_api(query, content)
        results[doc_name] = analysis
    return results

# Find the most relevant documents
def retrieve_relevant_docs(query, documents, top_k=3):
    try:
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
    except Exception as e:
        logging.error(f"Error retrieving relevant documents: {e}")
        return {}

# Main RAG workflow
def main():
    try:
        logging.info("Starting RAG system...")
        query = input("Enter your query or report: ").strip()
        if not query:
            logging.error("Query is empty. Please provide a valid input.")
            print("Error: Query cannot be empty.")
            return

        documents = load_documents()
        if not documents:
            print("Error: No documents found for analysis. Check the 'documents' directory.")
            return

        logging.info("Retrieving relevant documents...")
        relevant_docs = retrieve_relevant_docs(query, documents)
        if not relevant_docs:
            logging.warning("No relevant documents found for the query.")
            print("Warning: No relevant documents found for the query.")
            return

        logging.info("Checking compliance for relevant documents...")
        compliance_results = check_compliance(query, relevant_docs)

        print("\nCompliance Analysis:")
        for doc_name, result in compliance_results.items():
            print(f"\nDocument: {doc_name}\nResult: {result}")
        logging.info("RAG system completed successfully.")
    except Exception as e:
        logging.critical(f"Unexpected error in main workflow: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
