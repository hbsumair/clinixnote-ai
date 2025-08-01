import streamlit as st
from openai import OpenAI  

st.set_page_config(page_title="ClinixNote AI", layout="centered")
st.title("🩺 ClinixNote AI")
st.markdown("""
Enter patient details to generate a SOAP note and a discharge summary when needed.
""")

openai_api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

if not openai_api_key:
    st.warning("Please enter your API key to proceed.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# --- Patient info input ---
with st.form("patient_info_form"):
    st.subheader("📝 Patient Info")
    patient_name = st.text_input("Name")
    age = st.number_input("Age", 0, 120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    case_summary = st.text_area("Case Summary", height=200)
    submitted = st.form_submit_button("🧠 Generate Clinical Note")

if "patient_data" not in st.session_state:
    st.session_state.patient_data = {}

if submitted and case_summary.strip():
    prompt = f"""
You are a clinical AI. Given the following case, generate:

1. SOAP note (clearly labeled).
2. Differential diagnoses (3–5) with reasons.
3. A management plan including:
   - Medications (name, dose, frequency).
   - Follow-up timeline.
   - Alarming symptoms for which patient should return.

Patient Name: {patient_name}
Age: {age}
Gender: {gender}
Case Summary: {case_summary}
    """

    with st.spinner("Generating clinical note..."):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a clinical AI assistant helping doctors."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            result = response.choices[0].message.content
            st.session_state.patient_data = {
                "name": patient_name,
                "age": age,
                "gender": gender,
                "case_summary": case_summary,
                "ai_note": result
            }
            st.success("✅ Note generated!")
            st.markdown("---")
            st.markdown(result)
        except Exception as e:
            st.error(f"❌ Error: {e}")

# --- Discharge Summary Button ---
if st.session_state.get("patient_data"):
    if st.button("📄 Generate Discharge Summary"):
        discharge_prompt = f"""
You are a clinical AI. Based on the following case and clinical note, generate a discharge summary that includes:

- Final diagnosis
- Medications with name, dose, frequency
- Follow-up instructions
- Alarming symptoms that require urgent return

Case Summary: {st.session_state['patient_data']['case_summary']}
AI Clinical Note: {st.session_state['patient_data']['ai_note']}
        """
        with st.spinner("Creating discharge summary..."):
            try:
                discharge_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a clinical AI generating detailed discharge summaries."},
                        {"role": "user", "content": discharge_prompt}
                    ],
                    temperature=0.5
                )
                discharge_text = discharge_response.choices[0].message.content
                st.subheader("🏥 Discharge Summary")
                st.markdown(discharge_text)
            except Exception as e:
                st.error(f"❌ Error: {e}")

