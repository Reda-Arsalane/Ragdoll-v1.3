import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from rag_compliance import analyze_compliance  # Ensure this module is correctly located and imported

class RAGDollEUAIActs:
    def __init__(self, root):
        self.root = root
        self.root.title("RAGDoll_EUAIActs")
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        # Title Label
        title_label = tk.Label(root, text="RAGDoll_EUAIActs", font=("Helvetica", 18, "bold"))
        title_label.pack(pady=10)

        # Instructions
        instructions = tk.Label(root, text="Please answer the following questions about your AI-as-a-service product:")
        instructions.pack(pady=5)

        # Question Form
        self.form_frame = tk.Frame(root)
        self.form_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.questions = [
            "1. What is the primary purpose of your AI system, including its main features, deployment mode, and the geographic areas and languages it supports?",
            "2. Who are the key stakeholders for your AI system, and what are the potential benefits and harms it might create for them?",
            "3. Are there any known restricted, unsupported, or sensitive uses of your AI system, and what are the potential impacts of failures or misuse on stakeholders?",
            "4. What are the data requirements for your system, and how do you plan to mitigate potential harms, such as addressing fairness concerns or sensitive use cases?"
        ]
        self.entries = []

        for question in self.questions:
            question_label = tk.Label(self.form_frame, text=question, anchor="w", justify="left", wraplength=650)
            question_label.pack(fill="x", padx=5, pady=5)

            answer_entry = tk.Text(self.form_frame, height=3, width=80, wrap=tk.WORD)
            answer_entry.pack(padx=5, pady=5)
            self.entries.append(answer_entry)

        # Submit Button
        submit_button = tk.Button(root, text="Submit Query", command=self.submit_query)
        submit_button.pack(pady=10)

        # Results Section
        self.results_label = tk.Label(root, text="Compliance Analysis Results:", anchor="w", justify="left")
        self.results_label.pack(fill="x", padx=10, pady=5)

        self.results_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=12)
        self.results_text.pack(fill="both", expand=True, padx=10, pady=5)

    def submit_query(self):
        # Gather answers
        query = "\n".join(entry.get("1.0", tk.END).strip() for entry in self.entries if entry.get("1.0", tk.END).strip())
        if not query:
            messagebox.showerror("Error", "Please fill out all fields before submitting.")
            return

        # Call RAG Compliance
        try:
            self.results_text.delete(1.0, tk.END)  # Clear previous results
            self.results_text.insert(tk.END, "Processing...\n")

            # Debug: Ensure the query being sent is correct
            print(f"Query Sent to Backend:\n{query}\n")

            results = analyze_compliance(query, documents_directory="core\documents", top_k=5)

            # Debug: Ensure results are received from the backend
            print(f"Results from Backend:\n{results}\n")

            if not results:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "No results returned from the analysis.")
                return

            if "error" in results:
                messagebox.showerror("Error", results["error"])
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, results["error"])
                return
            
            # Display Results
            output = ""
            for doc, res in results.items():
                output += f"Document: {doc}\nResult: {res}\n\n"

            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, output)
            messagebox.showinfo("Success", "Analysis complete. See the results below.")
        except Exception as e:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"An unexpected error occurred: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# Run the Program
if __name__ == "__main__":
    root = tk.Tk()
    app = RAGDollEUAIActs(root)
    root.mainloop()
