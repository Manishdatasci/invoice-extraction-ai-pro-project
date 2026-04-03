# Invoice Extraction AI

## Overview

This project is an AI-powered application that extracts structured data from invoice images using OCR and stores it in Supabase. It also provides analytics insights on the extracted data.

---

## Tech Stack

* **Frontend & Backend:** Streamlit
* **OCR:** Tesseract
* **LLM:** OpenAI (with fallback handling)
* **Database & Storage:** Supabase

---

## Workflow

1. Upload invoice image
2. Extract text using OCR
3. Parse text into structured JSON (LLM / fallback)
4. Store data in Supabase
5. Display analytics dashboard

---

## Features

* Invoice data extraction
* JSON structured output
* Error handling with fallback mechanism
* Duplicate invoice detection
* Format detection
* Analytics:

  * Vendor-wise spend
  * Monthly trends
  * Currency-wise totals

---

## Assumptions

* Input invoices are clear images
* OCR accuracy depends on image quality
* LLM API may fail due to quota limits

---

## Limitations

* PDF support limited
* LLM fallback used when API is unavailable
* Advanced format learning not implemented

---

## Future Improvements

* Add FastAPI backend
* React frontend
* Better format detection
* Duplicate detection using ML
* Confidence score

---

## Note on API Usage

OpenAI API key is not included for security reasons.
Fallback mechanism is implemented to ensure system robustness.

---

## Analytics Dashboard

The app provides:

* Vendor spend analysis
* Monthly trends
* Total invoices processed

---

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Project Structure

```
invoice-ai/
│
├── app.py
├── requirements.txt
├── README.md
├── sample_invoice.png
```

---

## Author

Manish Kumar Rajak
