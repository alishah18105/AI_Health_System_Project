import pandas as pd
import pytesseract
from PIL import Image
import re
import os
import pdfplumber
from pdf2image import convert_from_path
from test_name_map import test_name_map
from remarks_rules import generate_remarks

# Path to Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load CBC reference dataset
REFERENCE_FILE = "data/cbc_reference_dataset.csv"
reference_df = pd.read_csv(REFERENCE_FILE)
reference_df['test'] = reference_df['test'].str.strip().str.upper()


# ✅ Utility functions
def normalize_test_name(raw: str) -> str:
    raw = raw.lower().replace("-", " ").replace("_", " ")
    raw = raw.replace("/", "")   # remove slash but keep digits
    raw = re.sub(r'[^a-z0-9\s%]', '', raw)  # keep alphanum + %
    raw = re.sub(r'\s+', ' ', raw).strip()

    if "nrbc100wbc" in raw:
        return "NRBC/100WBC"

    return test_name_map.get(raw, None)


def standardize_test_name(raw):
    raw = raw.strip().upper()
    raw = raw.replace(".", "").replace("%", "")  

    mapping = {
        "HB": "HEMOGLOBIN",
        "RBC": "RED BLOOD CELLS",
        "HCT": "HEMATOCRIT",
        "MCV": "MEAN CORPUSCULAR VOLUME",
        "MCH": "MEAN CORPUSCULAR HEMOGLOBIN",
        "MCHC": "MEAN CORPUSCULAR HEMOGLOBIN CONCENTRATION",
        "WBC": "WHITE BLOOD CELLS",
        "PLATELETS": "PLATELETS",
        "NEUTROPHILS": "NEUTROPHILS",
        "LYMPHOCYTES": "LYMPHOCYTES",
        "MONOCYTES": "MONOCYTES",
        "EOSINOPHILS": "EOSINOPHILS",
        "BASOPHILS": "BASOPHILS",
        "NRBC/100WBC": "NRBC/100WBC"
    }
    return mapping.get(raw, None)


def safe_float_conversion(value_str, low, high):
    try:
        value = float(value_str)
    except ValueError:
        return None

    if value > 200 and high < 200:
        value = value / 10  
    if value > 2000 and high < 2000:
        value = value / 100  
    return value


def extract_text_from_pdf(file_path):
    """Try extracting text from PDF. If empty, fallback to OCR via images."""
    text = ""

    # First try pdfplumber (works if text layer exists)
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    if text.strip():
        return text  

    # Fallback: scanned PDF → OCR
    images = convert_from_path(file_path, poppler_path=r"C:\Program Files\poppler\Library\bin")
    for img in images:
        text += pytesseract.image_to_string(img) + "\n"

    return text


def extract_text(file_path):
    """Extract text from image or PDF."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".jpg", ".jpeg", ".png"]:
        return pytesseract.image_to_string(Image.open(file_path))
    elif ext == ".pdf":
        return extract_text_from_pdf(file_path)
    else:
        raise ValueError("Unsupported file format")


def analyze_cbc_report(file_path):
    """Extract values from CBC report (image/pdf) and analyze"""
    text = extract_text(file_path)
    results = []

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue

        match = re.match(r"^([A-Za-z0-9/%\.]+)\s+([0-9.,]+)", line)
        if not match:
            continue

        raw_name = match.group(1)
        value_str = match.group(2).rstrip('.').replace(",", "")

        standardized_name = standardize_test_name(raw_name)
        if not standardized_name:
            continue

        ref = reference_df[reference_df['test'] == standardized_name]
        if ref.empty:
            continue

        low = float(ref.iloc[0]['low'])
        high = float(ref.iloc[0]['high'])
        unit = ref.iloc[0]['unit'] if 'unit' in ref.columns else ""

        value = safe_float_conversion(value_str, low, high)
        if value is None:
            continue

        if value < low:
            status = "Low"
        elif value > high:
            status = "High"
        else:
            status = "Normal"

        results.append({
            "Test": standardized_name,
            "Value": value,
            "Unit": unit,
            "Normal_Range": f"{low} - {high}",
            "Status": status
        })

    remarks = generate_remarks(results)
    return results, remarks


# 🔹 Example Usage
if __name__ == "__main__":
    results, remarks = analyze_cbc_report("cbc_report_sample.pdf")  # now supports pdf & image

    print("=== CBC RESULTS ===")
    for r in results:
        print(f"{r['Test']}: {r['Value']} {r['Unit']} "
              f"(Normal: {r['Normal_Range']}) → {r['Status'].lower()}")

    print("\n=== REMARKS ===")
    for rem in remarks:
        print("-", rem)
