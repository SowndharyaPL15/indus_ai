import os
from .pdf_loader import extract_pdf
from .docx_loader import extract_docx
from .csv_loader import extract_csv
from .excel_loader import extract_excel
from .image_loader import extract_image
from .text_loader import extract_text

def extract_text_from_file(file_path: str, file_type: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    
    if file_type == "application/pdf" or ext == ".pdf":
        return extract_pdf(file_path)
    elif "wordprocessingml" in file_type or ext == ".docx":
        return extract_docx(file_path)
    elif "csv" in file_type or ext == ".csv":
        return extract_csv(file_path)
    elif "spreadsheetml" in file_type or "excel" in file_type or ext in [".xls", ".xlsx"]:
        return extract_excel(file_path)
    elif file_type.startswith("image/") or ext in [".png", ".jpg", ".jpeg"]:
        return extract_image(file_path)
    elif file_type.startswith("text/") or ext == ".txt":
        return extract_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type} / {ext}")
