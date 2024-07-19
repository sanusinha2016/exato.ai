# Task 1
import PyPDF2
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("exato-96bee-firebase-adminsdk-dft36-5a8af47540.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        pdf_text = {}
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            pdf_text[f"Page_{page_num + 1}"] = text
    return pdf_text

pdf_path = "pritul.pdf"

pdf_text = extract_text_from_pdf(pdf_path)

document = {
    "file_name": pdf_path,
    "text_content": pdf_text
}

document_id = pdf_path.split('.')[0]

db.collection("Task 1").document(document_id).set(document)

print("PDF text successfully stored in Firestore.")
