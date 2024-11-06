from docx import Document
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import os

# Define the character sets and their respective indices
urdu_alphabet = "ا ب پ ت ٹ ث ج چ ح خ د ڈ ذ ر ڑ ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن و ہ ء ی ے"
char_indices = {char: idx+1 for idx, char in enumerate(urdu_alphabet.split())}

# Data augmentation functions
def apply_erosion(image):
    kernel = np.ones((2, 2), np.uint8)
    return cv2.erode(np.array(image), kernel, iterations=1)

def apply_dilation(image):
    kernel = np.ones((2, 2), np.uint8)
    return cv2.dilate(np.array(image), kernel, iterations=1)

def apply_rotation(image, angle=15):
    return image.rotate(angle, expand=True)

def apply_shear(image, shear=0.2):
    width, height = image.size
    m = np.array([
        [1, shear, 0],
        [0, 1, 0]
    ], dtype=np.float32)
    image = image.transform((width, height), Image.AFFINE, m.flatten(), resample=Image.BICUBIC)
    return image

# Function to save images with appropriate naming convention
def save_image(word, image, aug_type, output_dir):
    indices = '_'.join(str(char_indices[char]) for char in word)
    name = f"{len(word)}_{indices}_{aug_type}.png"
    image.save(os.path.join(output_dir, name))

# Load the Word document
doc = Document('urdu_words.docx')

# Create output directory
output_dir = 'images_from_word'
os.makedirs(output_dir, exist_ok=True)

# Set the font (ensure the path to the font is correct)
font_path = "Jameel Noori Nastaleeq Regular.ttf"  # Update this path to the correct font file location
font_size = 40
font = ImageFont.truetype(font_path, font_size)

# Process each word in the document
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print("Cell is here: ", cell)
            word = cell.text.strip()
            if word:
                print("Word is Here", word)
                try:
                    # Create an image of the word
                    img = Image.new('RGB', (150, 100), color='white')
                    d = ImageDraw.Draw(img)
                    bbox = d.textbbox((0, 0), word, font=font)
                    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    text_x = (img.width - text_width) // 2
                    text_y = (img.height - text_height) // 2
                    d.text((text_x, text_y), word, fill='black', font=font)

                    # Save original image
                    save_image(word, img, 'none', output_dir)

                    # Apply and save augmentations
                    erosion_img = Image.fromarray(apply_erosion(img))
                    save_image(word, erosion_img, 'erosion', output_dir)

                    dilation_img = Image.fromarray(apply_dilation(img))
                    save_image(word, dilation_img, 'dilation', output_dir)

                    rotation_img = apply_rotation(img)
                    save_image(word, rotation_img, 'rotation', output_dir)

                    shear_img = apply_shear(img)
                    save_image(word, shear_img, 'shear', output_dir)

                except Exception as e:
                    print(f"Failed to process word '{word}': {e}")

