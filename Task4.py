import cv2
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import firebase_admin
from firebase_admin import credentials, storage
import os
import urllib.request
from urllib.error import HTTPError

cred = credentials.Certificate('exato-96bee-firebase-adminsdk-dft36-5a8af47540.json')
firebase_admin.initialize_app(cred, {'storageBucket': 'exato-96bee.appspot.com'})

def download_image(blob, download_path):
    try:
        image_data = blob.download_as_string()
        with open(download_path, 'wb') as f:
            f.write(image_data)
    except Exception as e:
        print(f"Error: {e}")

def match_images(user_image_path):
    bucket = storage.bucket()
    blobs = bucket.list_blobs()
    user_img = cv2.imread(user_image_path)
    user_img = cv2.cvtColor(user_img, cv2.COLOR_BGR2GRAY)
    user_img = cv2.resize(user_img, (300, 300))

    for blob in blobs:
        if blob.content_type and blob.content_type.startswith('image/'):
            local_image_path = 'temp_image'
            download_image(blob, local_image_path)

            # Read the downloaded image
            img = cv2.imread(local_image_path)
            if img is None:
                print(f"Failed to read image {blob.name}")
                continue
            
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.resize(img, (300, 300))

            # similarity by ssim , structure similarity index measure....
            similarity = ssim(user_img, img)
            similarity_value = similarity * 100
            print(f"Similarity with {blob.name} is {similarity_value}")

            # Display........................
            plt.subplot(1, 2, 1)
            plt.imshow(user_img, cmap='gray')
            plt.title('User Image')
            plt.subplot(1, 2, 2)
            plt.imshow(img, cmap='gray')
            plt.title('Firebase Image')
            plt.show()

            if similarity_value >= 99.99:
                print(f"Signature Matched with {blob.name}")
                os.remove(local_image_path)
                return

            os.remove(local_image_path)

    print("No matching image found.")
user_image_path = "2.webp"
match_images(user_image_path)
