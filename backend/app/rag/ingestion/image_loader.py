from PIL import Image
import pytesseract

def extract_image(file_path: str) -> str:
    # Requires tesseract to be installed on the system
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text.strip()
