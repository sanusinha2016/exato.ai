import streamlit as st
from streamlit_option_menu import option_menu
import PyPDF2
import firebase_admin
from firebase_admin import credentials, firestore, storage
import re
import cv2
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import os
import numpy as np
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")

if not firebase_admin._apps:

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {'storageBucket': storage_bucket})

    cred = credentials.Certificate("key.json")
    firebase_admin.initialize_app(cred, {'storageBucket': 'exato-96bee.appspot.com'})


db = firestore.client()
bucket = storage.bucket()

selected = option_menu(
    menu_title=None, 
    options=["Task 1", "Task 2", "Task 3", "Task 4"], 
    icons=["file-earmark-text", "search", "list-task", "images"], 
    menu_icon="cast", 
    default_index=0, 
    orientation="horizontal",
)

def fetch_image_paths(folder_path):
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(image_extensions)]

def display_images_in_grid(image_paths, columns=3):
    num_images = len(image_paths)
    num_rows = (num_images + columns - 1) // columns  # Calculate number of rows needed
    
    selected_image = None

    for row in range(num_rows):
        cols = st.columns(columns)
        for col in range(columns):
            index = row * columns + col
            if index < num_images:
                with cols[col]:
                    img_path = image_paths[index]
                    img = Image.open(img_path)
                    if st.button(f"Select {os.path.basename(img_path)}", key=img_path):
                        selected_image = img_path
                    st.image(img, caption=os.path.basename(img_path), use_column_width=True)
            else:
                with cols[col]:
                    st.write("")

    return selected_image

def download_image(blob, download_path):
    try:
        image_data = blob.download_as_string()
        with open(download_path, 'wb') as f:
            f.write(image_data)
    except Exception as e:
        print(f"Error: {e}")

def match_images(user_image):
    user_img = cv2.imdecode(np.frombuffer(user_image, np.uint8), cv2.IMREAD_GRAYSCALE)
    user_img = cv2.resize(user_img, (300, 300))

    matched = False

    for blob in bucket.list_blobs():
        if blob.content_type and blob.content_type.startswith('image/'):
            local_image_path = 'temp_image'
            download_image(blob, local_image_path)

            img = cv2.imread(local_image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                print(f"Failed to read image {blob.name}")
                continue

            img = cv2.resize(img, (300, 300))
            similarity = ssim(user_img, img)
            similarity_value = similarity * 100

            if similarity_value >= 99.99:
                st.success(f"Signature Matched with {blob.name}")
                st.write(f"Similarity with {blob.name} is {similarity_value:.2f}%")

                fig, axes = plt.subplots(1, 2, figsize=(10, 5))
                axes[0].imshow(user_img, cmap='gray')
                axes[0].set_title('User Image')
                axes[1].imshow(img, cmap='gray')
                axes[1].set_title('Firebase Image')
                st.pyplot(fig)

                os.remove(local_image_path)
                matched = True
                break

            os.remove(local_image_path)

    if not matched:
        st.write("No matching image found.")

if selected == "Task 1":
    st.title("TASK 1 : PDF text extract and store into database (FIREBASE).")

    def extract_text_from_pdf(pdf_file):
        reader = PyPDF2.PdfReader(pdf_file)
        pdf_text = {}
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            pdf_text[f"Page_{page_num + 1}"] = text
        return pdf_text

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        with st.spinner('Extracting text from PDF...'):
            pdf_text = extract_text_from_pdf(uploaded_file)
            pdf_path = uploaded_file.name
            
            document = {
                "file_name": pdf_path,
                "text_content": pdf_text
            }
            
            document_id = pdf_path.split('.')[0]
            
            db.collection("Task 1").document(document_id).set(document)
            
            st.success("PDF text successfully stored in Firestore.")
            st.write("Handwritten PDF text successfully stored in Firestore.")

            st.subheader("Extracted Text")
            for page, text in pdf_text.items():
                st.write(f"**{page}:**")
                st.write(text)

elif selected == "Task 2":
    st.title("TASK 2 : Finding sentences containing words and store in database (FIREBASE). ")

    def extract_text_from_pdf(pdf_file):
        reader = PyPDF2.PdfReader(pdf_file)
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

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    words_input = st.text_input("Enter words to search for (comma-separated)", "and,of")

    if uploaded_file is not None and words_input:
        words = [word.strip() for word in words_input.split(",")]

        with st.spinner('Extracting text from PDF...'):
            pdf_text = extract_text_from_pdf(uploaded_file)
            pdf_path = uploaded_file.name
            
            sentences_with_words = extract_sentences_containing_words(pdf_text, words)

            document_id = pdf_path.split('.')[0]
            for word, sentences in sentences_with_words.items():
                document = {
                    "file_name": pdf_path,
                    "word": word,
                    "sentences": sentences
                }
                
                db.collection("Task 2").document(document_id).collection(word).document("data").set(document)
            
            st.success("Sentences containing specified words successfully stored in Firestore.")

            st.subheader("Extracted Sentences")
            for word, sentences in sentences_with_words.items():
                st.write(f"**Word: {word}**")
                for sentence in sentences:
                    st.write(f"- {sentence}")

elif selected == "Task 3":
    st.title("Task 3 : Extract the handwritten text from the PDF like Task-2 and persist into DB (FIREBASE)")
    st.header("This can't be run online, as it not configured with AWS for computing and packages management.")

elif selected == "Task 4":
    st.title("Signature matching from database.")

    st.subheader("Choose an Image Source")
    option = st.radio("Select image source", ["Select from Below Options","Upload Image", ])

    if option == "Upload Image":
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"])

        if uploaded_file is not None:
            with st.spinner('Matching images...'):
                user_image = uploaded_file.read()
                match_images(user_image)

    elif option == "Select from Below Options":
        st.subheader("Select a Signature Image")
        folder_path = './Signature List'
        image_paths = fetch_image_paths(folder_path)
        
        selected_image_path = display_images_in_grid(image_paths)

        if selected_image_path:
            st.write(f"Selected image for matching: {os.path.basename(selected_image_path)}")
            with open(selected_image_path, 'rb') as f:
                user_image = f.read()
                with st.spinner('Matching images...'):
                    match_images(user_image)
