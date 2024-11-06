import fitz  # PyMuPDF library for PDF processing
import cv2  # OpenCV for image processing (limited text extraction)
import numpy as np
from PIL import Image
import os
from itertools import product

# Define the character sets
start = ["ن"]
mid = ["ب", "ج", "س", "ص", "ط", "ع", "ف", "ق", "ک", "ل", "م", "ن", "ہ", "ی"]
end = ["ا", "ب", "ج", "د", "ر", "س", "ص", "ط", "ع", "ف", "ق", "ک", "ل", "م", "ن", "و", "ہ", "ی", "ے"]
urdu_alphabet = ["ا", "ب", "پ", "ت", "ٹ", "ث", "ج", "چ", "ح", "خ", "د", "ڈ", "ذ", "ر", "ڑ", "ز", "ژ", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ک", "گ", "ل", "م", "ن", "و", "ہ", "ء", "ی", "ے"]

# Define the augmentations
def apply_augmentations(image, techniques):
    augmented_images = []
    for technique in techniques:
        if technique == 'none':
            augmented_images.append((image, 'none'))
        elif technique == 'erosion':
            kernel = np.ones((3, 3), np.uint8)
            erosion = cv2.erode(image, kernel, iterations=1)
            augmented_images.append((erosion, 'erosion'))
        elif technique == 'dilation':
            kernel = np.ones((3, 3), np.uint8)
            dilation = cv2.dilate(image, kernel, iterations=1)
            augmented_images.append((dilation, 'dilation'))
        elif technique == 'rotation':
            rows, cols = image.shape[:2]
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), 10, 1)
            rotation = cv2.warpAffine(image, M, (cols, rows))
            augmented_images.append((rotation, 'rotation'))
        elif technique == 'shear':
            M = np.float32([[1, 0.2, 0], [0.2, 1, 0]])
            shear = cv2.warpAffine(image, M, (cols, rows))
            augmented_images.append((shear, 'shear'))
    return augmented_images

# Get character index from the Urdu alphabet
def get_char_index(char, alphabet):
    return alphabet.index(char) + 1

# Generate all possible 5-character words
words = []
for s in start:
    for mid_combo in product(mid, repeat=3):
        for e in end:
            word = s + "".join(mid_combo) + e
            words.append(word)

# Function to capture each word and save them as images
def capture_words_from_pdf(pdf_path, output_dir, cell_width, cell_height, start_x, start_y, col_count, augmentations, urdu_alphabet, words):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    total_pages = len(pdf_document)
    
    word_index = 0

    # Iterate through each page
    for page_number in range(total_pages):
        page = pdf_document[page_number]
        
        # Get page dimensions
        page_width = page.rect.width
        page_height = page.rect.height

        # Calculate the number of rows and columns
        num_rows = 7
        num_cols = col_count
        
        # Iterate through each cell and capture the content
        for row in range(num_rows):
            for col in range(num_cols):
                if word_index >= len(words):
                    break

                left = start_x + col * cell_width
                top = start_y + row * cell_height
                right = left + cell_width
                bottom = top + cell_height

                # Define the region and capture the image
                region = fitz.Rect(left, top, right, bottom)
                pix = page.get_pixmap(clip=region)

                if pix.width == 0 or pix.height == 0:
                    print(f"Empty region detected at page {page_number}, row {row}, col {col}. Skipping...")
                    continue

                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Check if image is empty
                if image is None:
                    print(f"Image is None at page {page_number}, row {row}, col {col}. Skipping...")
                    continue

                # Convert image to grayscale
                gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

                # Get the current word
                word = words[word_index]
                word_index += 1

                # Get character indexes and total number of characters
                char_indexes = [get_char_index(char, urdu_alphabet) for char in word]
                total_chars = len(word)
                
                # Process the word and save with augmentations
                for aug_image, aug_name in apply_augmentations(gray_image, augmentations):
                    index_str = "_".join(f"{idx:02d}" for idx in char_indexes)
                    output_filename = f"{total_chars:02d}_{index_str}_{aug_name}.png"
                    cv2.imwrite(os.path.join(output_dir, output_filename), aug_image)

# Define character list and augmentations
augmentations = ['none', 'erosion', 'dilation', 'rotation', 'shear']

# Parameters
pdf_path = "urdu_words.pdf"
output_dir = "images_from_pdf"
cell_width = 130
cell_height = 100
start_x = 10
start_y = 50
col_count = 4

capture_words_from_pdf(pdf_path, output_dir, cell_width, cell_height, start_x, start_y, col_count, augmentations, urdu_alphabet, words)
