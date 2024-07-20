import firebase_admin
from firebase_admin import credentials, firestore
from pikepdf import Pdf, PdfImage
import pytesseract
import cv2
import matplotlib.pyplot as plt


cred = credentials.Certificate("exato-96bee-firebase-adminsdk-dft36-339c13aed5.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


def extract_text_from_handwritten_pdf(pdf_path, image_path):
    old_pdf = Pdf.open(pdf_path)
    page = old_pdf.pages[0]
    raw_image = page.images['/X0']

    pdf_image = PdfImage(raw_image)
    pdf_image.extract_to(fileprefix=image_path)

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


pdf_path = "input/handimages.pdf"
image_path = "test1"


extracted_text = extract_text_from_handwritten_pdf(pdf_path, image_path)


document = {
    "file_name": pdf_path,
    "text_content": extracted_text
}


document_id = pdf_path.split('/')[-1].split('.')[0]


db.collection("Task 3").document(document_id).set(document)

print("Handwritten PDF text successfully stored in Firestore.")
