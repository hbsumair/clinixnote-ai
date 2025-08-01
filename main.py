# ClinixNote AI — Updated with Database and PDF Export
import streamlit as st
from openai import OpenAI
import pandas as pd
from fpdf import FPDF
import os

# --- SETUP ---
st.set_page_config(page_title="ClinixNote AI", layout="centered")
st.title("🩺 ClinixNote AI")

st.markdown("""
Enter patient details below. The AI will generate a SOAP note, differential diagnoses, and a discharge summary.
""")

# --- API Key Input ---
openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

# --- Stop app if no key ---
if not openai_api_key:
    st.warning("🔑 Please enter your OpenAI API key to continue.")
    st.stop()

# --- Initialize OpenAI client ---
client = OpenAI(api_key=openai_api_key)

# --- Patient Inputs ---
patient_name = st.text_input("Patient Name")
patient_number = st.text_input("Patient Phone Number")
final_diagnosis = st.text_input("Final Diagnosis (enter before generating discharge)")

patient_input = st.text_area("Paste Patient Case Summary", height=200)

# --- Generate Note ---
if st.button("🧠 Generate Clinical Note") and patient_input.strip():
    with st.spinner("Generating notes and diagnoses..."):
        prompt = f"""
You are an expert clinical assistant AI. Given this patient presentation, generate:
1. A SOAP note.
2. A list of 3–5 differential diagnoses with reasoning.
3. A brief discharge summary that EXCLUDES the final diagnosis. That will be added by the doctor manually later.

Patient Case:
{patient_input}
"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use GPT-3.5 for free tier
                messages=[
                    {"role": "system", "content": "You are a clinical AI assistant helping doctors generate structured medical notes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            output = response.choices[0].message.content
            st.markdown("---")
            st.markdown(output)

            # Save to CSV
            patient_record = {
                "Name": patient_name,
                "Phone": patient_number,
                "Case Summary": patient_input,
                "Final Diagnosis": final_diagnosis,
                "Generated Notes": output
            }

            df = pd.DataFrame([patient_record])
            if os.path.exists("patients.csv"):
                df.to_csv("patients.csv", mode="a", header=False, index=False)
            else:
                df.to_csv("patients.csv", index=False)

            st.success("✅ Patient data saved.")

            # --- PDF Export ---
            if st.button("📄 Export Discharge Summary as PDF"):
                pdf = FPDF()
                pdf.add_page()

                # Hospital Letterhead (Placeholder)
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, "Hospital Name Here", ln=True, align="C")
                pdf.set_font("Arial", '', 10)
                pdf.cell(200, 10, "Address | Contact | Email", ln=True, align="C")
                pdf.ln(10)

                # Patient Info
                pdf.set_font("Arial", '', 12)
                pdf.multi_cell(0, 10, f"Patient Name: {patient_name}\nPhone: {patient_number}\nFinal Diagnosis: {final_diagnosis}")
                pdf.ln(5)

                # Discharge
                pdf.multi_cell(0, 10, "AI-Generated Notes:\n" + output)

                pdf_file = f"{patient_name.replace(' ', '_')}_Discharge.pdf"
                pdf.output(pdf_file)

                with open(pdf_file, "rb") as file:
                    st.download_button(label="Download Discharge PDF", data=file, file_name=pdf_file)

        except Exception as e:
            st.error(f"❌ Error: {e}")

