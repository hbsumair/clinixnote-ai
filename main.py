import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import csv
import os

# Set up page
st.set_page_config(page_title="ClinixNote AI", layout="centered")
st.title("🩺 ClinixNote AI")

st.markdown("""
Enter the patient details below. The AI will generate a SOAP note and differential diagnoses.  
You can separately generate a discharge summary based on your final diagnosis.
""")

# Input API key
openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")
if not openai_api_key:
    st.warning("Please enter your API key to proceed.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# Patient input
st.subheader("Patient Info")
name = st.text_input("Patient Name")
phone = st.text_input("Phone Number")
patient_input = st.text_area("Paste Patient Case Summary", height=200)

# Save to local database
if name and phone:
    if not os.path.exists("patient_db.csv"):
        with open("patient_db.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Phone"])
    with open("patient_db.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, phone])

# Generate SOAP Note & DDx
if st.button("🧠 Generate Clinical Note") and patient_input.strip():
    with st.spinner("Generating notes and diagnoses..."):
        prompt = f"""
You are an expert clinical assistant AI. Given this patient presentation, generate:
1. A SOAP note.
2. A list of 3–5 differential diagnoses with reasoning.

Patient Case:
{patient_input}
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a clinical AI assistant helping doctors."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            output = response.choices[0].message.content
            st.markdown("---")
            st.markdown("### Clinical Note & Differential Diagnoses")
            st.markdown(output)
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Input Final Diagnosis for Discharge
st.subheader("📋 Discharge Summary Generator")
final_diagnosis = st.text_input("Final Diagnosis (required for discharge summary)")
if st.button("📄 Generate Discharge Summary") and final_diagnosis.strip():
    with st.spinner("Creating bilingual discharge summary..."):
        discharge_prompt = f"""
You are a hospital discharge assistant. Given the final diagnosis, generate a detailed discharge summary that includes:

1. Diagnosis
2. Medications (name, dosage, frequency, duration)
3. Follow-up timing
4. Alarming symptoms (reasons to urgently return)
5. English + Urdu translation in sections

Patient Name: {name}
Final Diagnosis: {final_diagnosis}
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a bilingual clinical AI assistant helping doctors write discharge summaries in English and Urdu."},
                    {"role": "user", "content": discharge_prompt}
                ],
                temperature=0.5
            )
            discharge_text = response.choices[0].message.content
            st.markdown("### 🏥 Discharge Summary")
            st.markdown(discharge_text)

            # Export to PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            for line in discharge_text.split("\n"):
                pdf.multi_cell(0, 10, txt=line)
            filename = f"{name.replace(' ', '_')}_discharge.pdf"
            pdf.output(f"/mnt/data/{filename}")
            st.success("PDF generated successfully!")
            st.download_button("⬇️ Download PDF", data=open(f"/mnt/data/{filename}", "rb"), file_name=filename)

        except Exception as e:
            st.error(f"❌ Error: {e}")
