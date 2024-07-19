import firebase_admin
from firebase_admin import credentials, firestore
from pikepdf import Pdf, PdfImage
import pytesseract
import cv2
import matplotlib.pyplot as plt

# Initialize Firebase Admin SDK
cred = credentials.Certificate("exato-96bee-firebase-adminsdk-dft36-5a8af47540.json")
firebase_admin.initialize_app(cred)

# Create a Firestore client
db = firestore.client()

# Function to extract text from a handwritten PDF
def extract_text_from_handwritten_pdf(pdf_path, image_path):
    old_pdf = Pdf.open(pdf_path)
    page = old_pdf.pages[0]
    raw_image = page.images['/X0']

    pdf_image = PdfImage(raw_image)
    pdf_image.extract_to(fileprefix=image_path)
    # print(list(page.images.keys()))
    print("processing")

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  

    image = cv2.imread(image_path + '.jpg')
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_image = cv2.medianBlur(gray_image, 3)  # Remove noise
    _, binary_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # Binarize the image

    plt.imshow(binary_image, cmap='gray')
    plt.title('Processed Handwritten Image')
    plt.axis('off')
    plt.show()

    text = pytesseract.image_to_string(binary_image)

    return text

# Path to the handwritten PDF file
pdf_path = "input/handimages.pdf"
image_path = "test1"

# Extract text from the handwritten PDF
extracted_text = extract_text_from_handwritten_pdf(pdf_path, image_path)

# Prepare the document to be inserted
document = {
    "file_name": pdf_path,
    "text_content": extracted_text
}

# Remove file extension for document ID (optional)
document_id = pdf_path.split('/')[-1].split('.')[0]

# Insert the document into Firestore with the PDF path as the document ID
db.collection("Task 3").document(document_id).set(document)

print("Handwritten PDF text successfully stored in Firestore.")
