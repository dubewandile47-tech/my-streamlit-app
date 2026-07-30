import streamlit as st
import time
import os
from groq import Groq # We using Groq - it's FREE and FAST

# ===== PAGE SETUP =====
st.set_page_config(page_title="JARVIS Pro SA", page_icon="🤖", layout="centered")

# ===== API KEY SETUP =====
# Get free key from https://console.groq.com/keys
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ===== CREDITS SYSTEM =====
if "credits" not in st.session_state:
    st.session_state.credits = 5 # Free 5 credits

# ===== 6 PROTOCOLS - FIXED NAMES =====
PROTOCOLS = {
    "Protocol 1": "The Closer: Be direct, persuasive, and push for action. Use South African slang.",
    "Protocol 2": "The Protector: Be safe, warn about scams, protect the user. Be caring.",
    "Protocol 3": "The Hustler: Give business ideas, money-making tips, be ambitious and practical.",
    "Protocol 4": "The Teacher: Explain things simply, step by step. Be patient.",
    "Protocol 5": "The Motivator: Be hype, motivational, push them to win. Use fire emojis 🔥",
    "Protocol 6": "The SA Intel: Give current SA job market data, salaries, and top companies hiring."
}

def ask_jarvis(prompt, protocol):
    if not client:
        return "Add your GROQ_API_KEY in Streamlit Cloud Settings first!"

    system_msg = f"You are JARVIS Pro SA. {protocol} Reply in English but use SA slang sometimes. Keep it short."

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.1-8b-instant", # Free and fast
        max_tokens=300,
    )
    return chat_completion.choices[0].message.content

# ===== HEADER =====
st.title("🤖 JARVIS Pro SA")
st.write("Your R1 AI Assistant for South Africans 🇿🇦")
col1, col2 = st.columns(2)
with col1:
    st.metric("Your Credits", st.session_state.credits)
with col2:
    if st.button("Buy R20 = 20 Credits"):
        st.link_button("Pay with Paystack", "https://paystack.com/buy/your-link") # Replace with your link

st.markdown("---")

# ===== FEATURE MENU - NOW 6 OPTIONS =====
feature = st.selectbox(
    "What do you need help with today?",
    ["1. CV & Cover Letter - Protocol 4", 
     "2. WhatsApp Reply Writer - Protocol 1",
     "3. Scam Checker - Protocol 2", 
     "4. Business Ideas - Protocol 3", 
     "5. Ask JARVIS Anything - Protocol 5",
     "6. SA Job Market Intel - Protocol 6"] # ADDED THIS
)

protocol_key = feature.split("- ")[1] # This now gives "Protocol 6"
protocol = PROTOCOLS.get(protocol_key, PROTOCOLS["Protocol 4"]) # SAFER - won't crash

# ===== MAIN INPUT =====
user_input = st.text_area("Tell JARVIS what you need:")

if st.button("Ask JARVIS"):
    if st.session_state.credits > 0:
        if not user_input:
            st.warning("Type something first")
        else:
            st.session_state.credits -= 1
            with st.spinner("JARVIS is thinking..."):
                time.sleep(1)
                response = ask_jarvis(user_input, protocol)
                st.success("JARVIS Response:")
                st.write(response)
    else:
        st.error("No credits left. Tap 'Buy R20 = 20 Credits' above")

# ===== FOOTER =====
st.markdown("---")
st.caption("JARVIS Pro SA | Powered by Groq AI | R1 per task")
