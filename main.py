# ClinixNote AI — MVP Skeleton
# A Streamlit-based app for generating SOAP notes, differentials, and discharge summaries from patient input

import streamlit as st
from openai import OpenAI  

# --- SETUP ---
st.set_page_config(page_title="ClinixNote AI", layout="centered")
st.title("🩺 ClinixNote AI")
st.markdown("""
Enter patient details below (via text). The AI will generate a SOAP note, differential diagnoses, and a discharge summary.
""")

# --- API Key Input ---
openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

# --- Stop app if no key ---
if not openai_api_key:
    st.warning("🔑 Please enter your OpenAI API key to continue.")
    st.stop()

# --- Initialize OpenAI client ---
client = OpenAI(api_key=openai_api_key)

# --- Text Input ---
patient_input = st.text_area("Paste Patient Case Summary", height=200)

if st.button("🧠 Generate Clinical Note") and patient_input.strip():
    with st.spinner("Generating notes and diagnoses..."):
        prompt = f"""
You are an expert clinical assistant AI. Given this patient presentation, generate:
1. A SOAP note.
2. A list of 3–5 differential diagnoses with reasoning.
3. A brief discharge summary.

Patient Case:
{patient_input}
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
