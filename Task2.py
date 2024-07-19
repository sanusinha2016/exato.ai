import PyPDF2
import firebase_admin
from firebase_admin import credentials, firestore
import re

cred = credentials.Certificate("exato-96bee-firebase-adminsdk-dft36-5a8af47540.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        pdf_text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            pdf_text += text
    return pdf_text

def extract_sentences_containing_words(text, words):
    sentences = re.split(r'(?<=[.!?]) +', text)
    word_sentences = {word: [] for word in words}
    
    for sentence in sentences:
        for word in words:
            if word in sentence:
                word_sentences[word].append(sentence.strip())
    
    return word_sentences

pdf_path = "cows.pdf"

pdf_text = extract_text_from_pdf(pdf_path)

words = ["and", "of"]

sentences_with_words = extract_sentences_containing_words(pdf_text, words)

document_id = pdf_path.split('.')[0]
for word, sentences in sentences_with_words.items():
    document = {
        "file_name": pdf_path,
        "word": word,
        "sentences": sentences
    }
    
    db.collection("Task 2").document(document_id).collection(word).document("data").set(document)

print("Sentences containing specified words successfully stored in Firestore.")
