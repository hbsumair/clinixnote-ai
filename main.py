# ClinixNote AI — MVP with Manual Final Diagnosis for Discharge
import streamlit as st
from openai import OpenAI

# --- SETUP ---
st.set_page_config(page_title="ClinixNote AI", layout="centered")
st.title("🩺 ClinixNote AI")
st.markdown("""
Enter patient details below. The AI will generate a SOAP note and differential diagnoses.  
You can then enter the **final diagnosis** to generate a discharge summary.
""")

# --- API Key Input ---
openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

# --- Stop app if no key ---
if not openai_api_key:
    st.warning("🔑 Please enter your OpenAI API key to continue.")
    st.stop()

# --- Initialize OpenAI client ---
client = OpenAI(api_key=openai_api_key)

# --- Patient Case Input ---
patient_input = st.text_area("Paste Patient Case Summary", height=200)

# --- Generate SOAP & Differentials ---
if st.button("🧠 Generate SOAP Note & Differentials") and patient_input.strip():
    with st.spinner("Generating clinical notes..."):
        prompt = f"""
You are a clinical AI assistant. From the following patient case, generate:

1. A detailed SOAP note (Subjective, Objective, Assessment, Plan).
2. A list of 3–5 differential diagnoses with reasoning.

Do NOT include any discharge summary or final diagnosis.

Patient Case:
{patient_input}
"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a clinical AI assistant helping doctors generate structured notes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            output = response.choices[0].message.content
            st.markdown("---")
            st.subheader("📋 Clinical Output")
            st.markdown(output)
        except Exception as e:
            st.error(f"❌ Error: {e}")

# --- Manual Final Diagnosis for Discharge Summary ---
st.markdown("---")
st.subheader("📝 Generate Discharge Summary")
final_diagnosis = st.text_input("Enter Final Diagnosis")

if st.button("📤 Generate Discharge Summary") and final_diagnosis.strip() and patient_input.strip():
    with st.spinner("Generating discharge summary..."):
        discharge_prompt = f"""
You are a clinical AI assistant. Using the following patient case and the final diagnosis provided by the doctor, generate a detailed discharge summary that includes:

1. Final diagnosis (provided below),
2. Medications prescribed (name, dose, frequency),
3. Follow-up instructions (e.g., when to return),
4. Alarming symptoms to return to the hospital for,
5. Any lifestyle or rehab advice.

Only generate the discharge summary. Do NOT repeat SOAP or differentials.

Patient Case:
{patient_input}

Final Diagnosis:
{final_diagnosis}
"""
        try:
            discharge_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a clinical AI assistant generating discharge summaries."},
                    {"role": "user", "content": discharge_prompt}
                ],
                temperature=0.5
            )
            discharge_output = discharge_response.choices[0].message.content
            st.markdown("### 🏥 Discharge Summary")
            st.markdown(discharge_output)
        except Exception as e:
            st.error(f"❌ Error: {e}")

