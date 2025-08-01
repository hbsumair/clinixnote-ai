import streamlit as st
from openai import OpenAI
import csv
import os
from datetime import datetime
from fpdf import FPDF

# --- PAGE SETUP ---
st.set_page_config(page_title="ClinixNote AI", layout="centered")
st.title("🩺 ClinixNote AI")

st.markdown("""
Enter patient details below. Generate SOAP notes, differential diagnoses, and a bilingual discharge summary.
""")

# --- OPENAI API KEY ---
openai_api_key = st.text_input("🔐 Enter your OpenAI API Key", type="password")
if not openai_api_key:
    st.warning("Please enter your OpenAI API key to continue.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# --- PATIENT INFO ---
st.subheader("👤 Patient Information")
patient_name = st.text_input("Patient Name")
patient_number = st.text_input("Phone Number")
patient_input = st.text_area("Case Summary", height=200)

# --- SAVE TO DATABASE ---
def save_to_csv(name, number):
    file_exists = os.path.isfile("patient_data.csv")
    with open("patient_data.csv", "a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Name", "Phone", "Date"])
        writer.writerow([name, number, datetime.now().strftime("%Y-%m-%d %H:%M")])

# --- CLINICAL NOTE ---
if st.button("🧠 Generate Clinical Note") and patient_input.strip():
    if not patient_name or not patient_number:
        st.error("⚠️ Please enter patient name and number.")
        st.stop()

    save_to_csv(patient_name, patient_number)

    with st.spinner("Generating SOAP note and differentials..."):
        prompt = f"""
You are a clinical AI. From the following patient case, generate:

1. SOAP Note
2. Differential diagnoses with reasons (3-5)

Case:
{patient_input}
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful AI doctor assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            output = response.choices[0].message.content
            st.markdown("### 📝 Clinical Note & Differentials")
            st.markdown(output)
        except Exception as e:
            st.error(f"❌ Error: {e}")

# --- DISCHARGE SUMMARY ---
st.subheader("🏥 Discharge Summary Generator")
final_diagnosis = st.text_input("Enter Final Diagnosis")
if st.button("📤 Generate Discharge Summary") and final_diagnosis and patient_name:
    with st.spinner("Generating bilingual discharge summary..."):
        discharge_prompt = f"""
Generate a detailed hospital discharge summary in both English and Urdu.

Include:
- Final Diagnosis: {final_diagnosis}
- Medications (name, dose, frequency, days)
- Follow-up timing
- Alarming symptoms for return
- Structure the Urdu section properly and label clearly.

Patient: {patient_name}
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a senior hospital discharge officer writing clear bilingual summaries."},
                    {"role": "user", "content": discharge_prompt}
                ],
                temperature=0.5
            )
            discharge_text = response.choices[0].message.content

            # --- PDF EXPORT ---
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
            pdf.set_font("DejaVu", size=12)

            for line in discharge_text.split('\n'):
                pdf.multi_cell(0, 10, txt=line)

            filename = f"discharge_{patient_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            pdf.output(filename)

            st.success("✅ Discharge summary generated.")
            with open(filename, "rb") as f:
                st.download_button(
                    label="📄 Download PDF",
                    data=f,
                    file_name=filename,
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"❌ Error: {e}")
