import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import os
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="ClinixNote AI", layout="centered")
st.title("🩺 ClinixNote AI")
st.markdown("Enter patient details below. The AI will generate SOAP notes, differentials, and discharge summaries.")

# --- Input API Key ---
openai_api_key = st.text_input("🔐 Enter your OpenAI API Key", type="password")
if not openai_api_key:
    st.warning("Please enter your API key.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# --- Local CSV for Patient Info ---
DB_FILE = "patients_db.csv"
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Name", "Phone", "Case Summary", "Final Diagnosis"])
    df_init.to_csv(DB_FILE, index=False)

# --- Patient Info Form ---
st.header("📄 Patient Case Input")
name = st.text_input("Patient Name")
phone = st.text_input("Phone Number")
case_summary = st.text_area("Case Summary", height=200)
final_diagnosis = st.text_input("Final Diagnosis (Enter before Discharge Summary)")

# Save patient info
if st.button("💾 Save Case"):
    if name and phone and case_summary:
        new_row = pd.DataFrame([[name, phone, case_summary, final_diagnosis]], columns=["Name", "Phone", "Case Summary", "Final Diagnosis"])
        new_row.to_csv(DB_FILE, mode="a", header=False, index=False)
        st.success("Patient case saved.")
    else:
        st.warning("Please enter Name, Phone, and Case Summary.")

# --- Generate Clinical Note ---
if st.button("🧠 Generate Clinical Note"):
    if not case_summary.strip():
        st.warning("Please enter the case summary.")
        st.stop()

    with st.spinner("Generating notes and diagnoses..."):
        prompt = f"""
You are a clinical assistant AI. Based on this patient case, generate:
1. A SOAP note.
2. 3–5 differential diagnoses with brief reasoning.

Patient Case:
{case_summary}
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a clinical AI assistant helping doctors generate structured medical notes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            output = response.choices[0].message.content
            st.markdown("---")
            st.markdown(output)
        except Exception as e:
            st.error(f"❌ Error: {e}")

# --- Generate Discharge Summary ---
def generate_discharge_summary(case_summary, final_diagnosis):
    discharge_prompt = f"""
You are a medical assistant. Generate a bilingual (Urdu + English) discharge summary based on this final diagnosis and patient case.
Include:
- Diagnosis (heading)
- Treatment/Medication plan: drug names, dose, frequency, and duration
- Follow-up timing
- Alarming signs that warrant return

Case Summary: {case_summary}
Final Diagnosis: {final_diagnosis}
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a bilingual Urdu-English clinical assistant."},
            {"role": "user", "content": discharge_prompt}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content

def save_pdf_discharge(name, content):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()

    # Register the correct Unicode Urdu + English font
    pdf.add_font("Noto", "", "NotoNaskhArabic-Regular.ttf", uni=True)
    pdf.set_font("Noto", size=12)

    effective_width = pdf.w - 2 * pdf.l_margin

    # Write Urdu + English discharge summary line by line
    for paragraph in content.split('\n'):
        if paragraph.strip():
            try:
                pdf.multi_cell(w=effective_width, h=8, txt=paragraph, align='L')
            except Exception as e:
                print(f"Encoding error in line: {paragraph}")
        else:
            pdf.ln(4)  # line spacing

    filename = f"{name.replace(' ', '_')}_discharge.pdf"
    pdf.output(filename)
    return filename



if st.button("📤 Generate Discharge Summary"):
    if not final_diagnosis.strip():
        st.warning("Please enter final diagnosis first.")
        st.stop()
    if not case_summary.strip():
        st.warning("Please enter case summary first.")
        st.stop()

    with st.spinner("Generating discharge summary..."):
        try:
            summary = generate_discharge_summary(case_summary, final_diagnosis)
            st.markdown("---")
            st.markdown(summary)
            filepath = save_pdf_discharge(name or "patient", summary)
            with open(filepath, "rb") as f:
                st.download_button("⬇️ Download Discharge PDF", f, file_name=filepath)
        except Exception as e:
            st.error(f"❌ Error: {e}")

