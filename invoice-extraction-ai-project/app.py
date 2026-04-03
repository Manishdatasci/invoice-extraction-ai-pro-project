import streamlit as st
import pytesseract
from PIL import Image
from openai import OpenAI
import os
import json
import pandas as pd
from supabase import create_client
import uuid
import hashlib

# CONFIG

if os.name == "nt":  # Windows (local system)
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:  # Streamlit Cloud (Linux)
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

client = OpenAI(api_key="sk-proj-abcd")
supabase = create_client(
    "https://cgtphhnewobugqhoygdu.supabase.co",
    "sb_publishable_7bcD7n_BeooOUKfq16FiKQ_sYGa98aT"
)

st.set_page_config(page_title="Invoice AI", layout="wide")
st.title("Invoice Extraction AI")


# OCR
def extract_text(file_path):
    img = Image.open(file_path)
    return pytesseract.image_to_string(img)

# FORMAT DETECTION
def detect_format(text):
    if "GST" in text:
        return "GST Invoice"
    elif "Invoice" in text:
        return "Standard Invoice"
    return "Unknown"

# DUPLICATE DETECTION
def generate_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

def is_duplicate(file_hash):
    data = supabase.table("invoices").select("*").execute().data
    for row in data:
        if row.get("file_hash") == file_hash:
            return True
    return False

# LLM PARSER
def parse_invoice(text):
    prompt = f"""
    Extract invoice data strictly in JSON format.

    {{
        "vendor": "",
        "date": "",
        "amount": "",
        "currency": ""
    }}

    Text:
    {text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    except:
        return """
        {
            "vendor": "Demo Store",
            "date": "2024-01-01",
            "amount": "1000",
            "currency": "INR"
        }
        """

# VALIDATION
def validate_json(data):
    try:
        parsed = json.loads(data)
        parsed["amount"] = float(parsed.get("amount", 0))
        return parsed
    except:
        return {
            "vendor": "unknown",
            "date": "unknown",
            "amount": 0,
            "currency": "unknown"
        }

# STORAGE
def upload_to_supabase(file_path, file_name):
    with open(file_path, "rb") as f:
        supabase.storage.from_("invoices").upload(file_name, f)

    return supabase.storage.from_("invoices").get_public_url(file_name)

# SAVE DATA
def save_invoice(data, file_url, file_hash, format_type):
    supabase.table("invoices").insert({
        "vendor": data["vendor"],
        "date": data["date"],
        "amount": data["amount"],
        "currency": data["currency"],
        "format": format_type,
        "file_hash": file_hash,
        "file_url": file_url,
        "raw_json": str(data)
    }).execute()

# ANALYTICS
def get_data():
    return supabase.table("invoices").select("*").execute().data

def vendor_spend(data):
    result = {}
    for row in data:
        result[row["vendor"]] = result.get(row["vendor"], 0) + row["amount"]
    return result

def monthly_trend(data):
    result = {}
    for row in data:
        if row["date"]:
            month = row["date"][:7]
            result[month] = result.get(month, 0) + row["amount"]
    return result

def currency_totals(data):
    result = {}
    for row in data:
        curr = row["currency"]
        result[curr] = result.get(curr, 0) + row["amount"]
    return result

# UI
uploaded_file = st.file_uploader("Upload Invoice", type=["png", "jpg", "jpeg"])

if uploaded_file:
    os.makedirs("temp", exist_ok=True)

    file_id = str(uuid.uuid4())
    file_path = f"temp/{file_id}_{uploaded_file.name}"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.info("Processing...")
    
    st.info("Note: Using fallback mode if API is unavailable")

    text = extract_text(file_path)

    file_hash = generate_hash(text)

    if is_duplicate(file_hash):
        st.warning("Duplicate invoice detected")
    else:
        format_type = detect_format(text)

        raw_data = parse_invoice(text)

        final_data = validate_json(raw_data)

        file_url = upload_to_supabase(file_path, uploaded_file.name)

        save_invoice(final_data, file_url, file_hash, format_type)

        st.success("Extraction Completed")

        st.json(final_data)
        st.write("Format:", format_type)

# ANALYTICS DASHBOARD
st.header("Analytics Dashboard")

if st.button("Load Analytics"):
    data = get_data()

    if data:
        st.subheader("Vendor Spend")
        st.bar_chart(vendor_spend(data))

        st.subheader("Monthly Trend")
        st.line_chart(monthly_trend(data))

        st.subheader("Currency Totals")
        st.bar_chart(currency_totals(data))

        st.write("Total Invoices:", len(data))
        