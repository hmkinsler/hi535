import os
from pdf2image import convert_from_path
import tesserocr
from PIL import Image
import cv2
import numpy as np

# Directory where PDFs are stored
pdf_dir = r'ocr_input'
# Directory where OCR results will be saved
output_dir = r'ocr_output'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

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

# Process each PDF in the directory
for pdf_file in os.listdir(pdf_dir):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        print(f"Processing {pdf_file}")

        # Convert PDF to image (each page is an image)
        images = convert_from_path(pdf_path)

        # Initialize an empty string to store the OCR results
        text = ""
        
        # Process each page
        for page_num, image in enumerate(images):
            print(f"Processing page {page_num + 1}")

            # Preprocess the image
            processed_image = preprocess_image(image)

            # Use Tesseract to perform OCR on the pre-processed image
            page_text = tesserocr.image_to_text(processed_image)

            # Append the text of the current page to the final output
            text += page_text

        # Save the OCR'd text into a text file
        output_file = os.path.join(output_dir, f"{os.path.splitext(pdf_file)[0]}.txt")
        with open(output_file, "w", encoding="utf-8") as text_file:
            text_file.write(text)

        print(f"OCR complete for {pdf_file}, saved to {output_file}")
