import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
from utils.directories import map_dir, map_output

# Ensure output directory exists
os.makedirs(map_output, exist_ok=True)

# Preprocessing function: Grayscale, Thresholding, and Denoising
def preprocess_image(image):
    # Convert PIL image to OpenCV format (numpy array)
    open_cv_image = np.array(image)

    # Convert to grayscale
    gray_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

    # Apply binary thresholding (Binarization)
    _, binary_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)

    # Apply denoising (optional, but can help with noisy scans)
    denoised_image = cv2.fastNlMeansDenoising(binary_image, None, 30, 7, 21)

    # Convert back to PIL Image format (Tesseract works with PIL images)
    final_image = Image.fromarray(denoised_image)
    
    return final_image

for file in os.listdir(map_dir):

    # Convert PDF to image
    image = convert_from_path(file)

    # Load the image
    image = cv2.imread(image)

    # Preprocess the image
    processed_image = preprocess_image(image)

    # Save the preprocessed image
    cv2.imwrite(os.path.join(map_output, f"processed_{image}"), processed_image)