import pandas as pd

def extract_excel(file_path: str) -> str:
    df = pd.read_excel(file_path)
    return df.to_string()
