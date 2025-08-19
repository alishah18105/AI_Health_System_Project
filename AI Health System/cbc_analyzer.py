import pandas as pd
import pytesseract
from PIL import Image
import re
from test_name_map import test_name_map
from remarks_rules import generate_remarks

# Path to Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load CBC reference dataset
REFERENCE_FILE = "cbc_reference_dataset.csv"
reference_df = pd.read_csv(REFERENCE_FILE)
reference_df['test'] = reference_df['test'].str.strip().str.upper()

# ✅ Test Name Mapping
def normalize_test_name(raw: str) -> str:
    raw = raw.lower().replace("-", " ").replace("_", " ")
    raw = raw.replace("/", "")   # remove slash but keep digits
    raw = re.sub(r'[^a-z0-9\s%]', '', raw)  # keep alphanum + %
    raw = re.sub(r'\s+', ' ', raw).strip()

    # Special handling
    if "nrbc100wbc" in raw:
        return "NRBC/100WBC"

    return test_name_map.get(raw, None)


def standardize_test_name(raw):
    raw = raw.strip().upper()
    raw = raw.replace(".", "").replace("%", "")  # remove trailing symbols

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
    """Convert OCR string to float with error correction"""
    try:
        value = float(value_str)
    except ValueError:
        return None

    # Heuristic correction for OCR mistakes
    if value > 200 and high < 200:
        value = value / 10  # e.g. 341 → 34.1
    if value > 2000 and high < 2000:
        value = value / 100  # e.g. 12500 → 125.0

    return value

def analyze_cbc_report(image_path):
    """Extract values from CBC report image and analyze"""
    text = pytesseract.image_to_string(Image.open(image_path))
    
    results = []

    for line in text.split("\n"):
        line = line.strip()
        #print("LINE:", line)

        if not line:
            continue

        # Extract test name + number
        match = re.match(r"^([A-Za-z0-9/%\.]+)\s+([0-9.,]+)", line)
        if not match:
            continue

        raw_name = match.group(1)  # now only HB, RBC, WBC, NRBC/100WBC etc.
        value_str = match.group(2).rstrip('.').replace(",", "")
        print("RAW:", raw_name, "→ STD:", standardize_test_name(raw_name), "→ VALUE:", value_str)

        
        standardized_name = standardize_test_name(raw_name)
        if not standardized_name:
            continue

        ref = reference_df[reference_df['test'] == standardized_name]
        if ref.empty:
            continue

        low = float(ref.iloc[0]['low'])
        high = float(ref.iloc[0]['high'])
        unit = ref.iloc[0]['unit'] if 'unit' in ref.columns else ""

        try:
            value = safe_float_conversion(value_str, low, high)
        except ValueError:
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

    # After collecting results → add remarks
    remarks = generate_remarks(results)
    return results, remarks

# 🔹 Rule-Based Remark Generator

# 🔹 Example Usage
if __name__ == "__main__":
    results, remarks = analyze_cbc_report("cbc_report_sample.jpg")

    print("=== CBC RESULTS ===")
    for r in results:
        print(f"{r['Test']}: {r['Value']} {r['Unit']} "
          f"(Normal: {r['Normal_Range']}) → {r['Status'].lower()}")

    print("\n=== REMARKS ===")
    for rem in remarks:
        print("-", rem)
