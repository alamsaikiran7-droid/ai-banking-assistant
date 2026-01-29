import streamlit as st
import os
from groq import Groq
from db_config import get_connection

# ================= CONFIG =================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AI Banking Assistant", page_icon="🏦", layout="wide")

# ================= CSS THEME =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom, #eaf3ff, #ffffff);
}

.title-text {
    font-size: 40px;
    font-weight: 700;
    color: #2b2f4c;
}

.subtitle-text {
    font-size: 18px;
    color: #6c7aa1;
}

.chat-user {
    background: #e8f5e9;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
}

.chat-ai {
    background: #eef2ff;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
}

input {
    border-radius: 15px !important;
}

button {
    border-radius: 12px !important;
    background-color: #4CAF50 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ================= DB FETCH =================
def get_bank_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    cursor.execute("SELECT * FROM loans")
    loans = cursor.fetchall()

    cursor.execute("SELECT * FROM procedures")
    procedures = cursor.fetchall()

    conn.close()
    return customers, loans, procedures


customers, loans, procedures = get_bank_data()

# loan count
loan_customers = set([loan[1] for loan in loans])  # customer_id
loan_count = len(loan_customers)

# procedure count
procedure_count = len(procedures)

bank_data = f"""
CUSTOMERS: {customers}
LOANS: {loans}
PROCEDURES: {procedures}
"""

# ================= UI LAYOUT =================
col1, col2, col3 = st.columns([1.3, 2, 1])

with col1:
    st.image("robot.png", width=330)
    st.image("customers.png", width=330)

with col2:
    st.markdown("<div class='title-text'>🏦 AI Banking Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle-text'>Groq + MySQL powered smart assistant</div>", unsafe_allow_html=True)

    # session state
    def submit_query():
        st.session_state.ask = True

    if "ask" not in st.session_state:
        st.session_state.ask = False

    if "question_input" not in st.session_state:
        st.session_state.question_input = ""

    question = st.text_input(
        "Enter your question:",
        key="question_input",
        on_change=submit_query
    )

    col_btn1, col_btn2 = st.columns([1,1])

    with col_btn1:
        ask = st.button("Ask AI")

    with col_btn2:
        clear = st.button("Clear")

    if ask:
        st.session_state.ask = True

    if clear:
        st.session_state.pop("question_input", None)
        st.session_state.ask = False
        st.rerun()


with col3:
    # Customer block
    st.markdown(f"""
    <div style="background:white;padding:8px 10px;border-radius:12px;
    box-shadow:0 2px 6px rgba(0,0,0,0.08);text-align:center;width:160px;margin:10px auto;">
        <div style="font-size:14px;font-weight:600;color:#4b3f72;">👤 Customer</div>
        <div style="font-size:22px;font-weight:700;margin-top:3px;color:#2b2f4c;">
            {len(customers)}
        </div>
        <div style="font-size:11px;color:#7a7a9d;">Total Customers</div>
    </div>
    """, unsafe_allow_html=True)

    # Loans block
    st.markdown(f"""
    <div style="background:white;padding:8px 10px;border-radius:12px;
    box-shadow:0 2px 6px rgba(0,0,0,0.08);text-align:center;width:160px;margin:10px auto;">
        <div style="font-size:14px;font-weight:600;color:#4b3f72;">💳 Loans</div>
        <div style="font-size:22px;font-weight:700;margin-top:3px;color:#2b2f4c;">
            {loan_count}
        </div>
        <div style="font-size:11px;color:#7a7a9d;">Customers with Loans</div>
    </div>
    """, unsafe_allow_html=True)

    # Guide block
    st.markdown(f"""
    <div style="background:white;padding:8px 10px;border-radius:12px;
    box-shadow:0 2px 6px rgba(0,0,0,0.08);text-align:center;width:160px;margin:10px auto;">
        <div style="font-size:14px;font-weight:600;color:#4b3f72;">📘 Guide</div>
        <div style="font-size:20px;font-weight:700;margin-top:3px;color:#2b2f4c;">
            AI Help
        </div>
        <div style="font-size:11px;color:#7a7a9d;">Ask about bank rules</div>
    </div>
    """, unsafe_allow_html=True)

    # Procedure block
    st.markdown(f"""
    <div style="background:white;padding:8px 10px;border-radius:12px;
    box-shadow:0 2px 6px rgba(0,0,0,0.08);text-align:center;width:160px;margin:10px auto;">
        <div style="font-size:14px;font-weight:600;color:#4b3f72;">📄 Procedure</div>
        <div style="font-size:22px;font-weight:700;margin-top:3px;color:#2b2f4c;">
            {procedure_count}
        </div>
        <div style="font-size:11px;color:#7a7a9d;">Bank Services</div>
    </div>
    """, unsafe_allow_html=True)

# ================= AI RESPONSE =================
if st.session_state.ask:
    if question.strip() == "":
        st.warning("Please enter a question")
    else:
        st.markdown(f"<div class='chat-user'>{question}</div>", unsafe_allow_html=True)

        prompt = f"""
You are an AI banking assistant.
If the answer is not present, say: "Data not available in database."

DATA:
{bank_data}

QUESTION:
{question}
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a banking assistant"},
                    {"role": "user", "content": prompt}
                ]
            )

            answer = response.choices[0].message.content
            st.markdown(f"<div class='chat-ai'>{answer}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error("AI service error. Check API key or model.")
            st.write(e)

    st.session_state.ask = False

# ================= FOOTER =================
st.markdown("""
<style>
.footer-marquee {
    position: fixed;
    bottom: 0;
    width: 100%;
    background: #1f2937;
    padding: 8px 0;
    overflow: hidden;
    white-space: nowrap;
    z-index: 999;
}

.footer-marquee span {
    display: inline-block;
    padding-left: 100%;
    animation: marquee 18s linear infinite, colorchange 4s linear infinite;
    font-size: 14px;
    font-weight: 600;
}

@keyframes marquee {
    0%   { transform: translateX(0%); }
    100% { transform: translateX(-100%); }
}

@keyframes colorchange {
    0%   { color: #22c55e; }
    25%  { color: #3b82f6; }
    50%  { color: #a855f7; }
    75%  { color: #f97316; }
    100% { color: #22c55e; }
}
</style>

<div class="footer-marquee">
    <span>
        🏦 This is AI Banking Assistant which helps you to know the queries about the bank — Ask about customers, loans, and bank procedures.
    </span>
</div>
""", unsafe_allow_html=True)
