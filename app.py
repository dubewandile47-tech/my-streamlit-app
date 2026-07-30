import streamlit as st
from groq import Groq
import json
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

st.set_page_config(page_title="JARVIS SA Pro", page_icon="🤖")
st.title("🤖 JARVIS SA Pro - Google Drive Memory")

MEMORY_FILE = "jarvis_memory.json"
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# GOOGLE DRIVE SETUP
def get_drive_service():
    if 'credentials' not in st.session_state:
        st.warning("Please connect Google Drive first 👇")
        return None
    creds = Credentials(**st.session_state.credentials)
    return build('drive', 'v3', credentials=creds)

def load_memory_from_drive():
    service = get_drive_service()
    if not service: return {"name":"", "phone":"", "email":"", "exp":"", "loc":"Rustenburg", "history":[]}
    
    results = service.files().list(q=f"name='{MEMORY_FILE}'", spaces='drive').execute()
    if not results.get('files'): return {"name":"", "phone":"", "email":"", "exp":"", "loc":"Rustenburg", "history":[]}
    
    file_id = results['files'][0]['id']
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return json.loads(fh.getvalue().decode())

def save_memory_to_drive(data):
    service = get_drive_service()
    if not service: return
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f)
    media = MediaFileUpload(MEMORY_FILE, mimetype='application/json')
    
    results = service.files().list(q=f"name='{MEMORY_FILE}'", spaces='drive').execute()
    if results.get('files'):
        service.files().update(fileId=results['files'][0]['id'], media_body=media).execute()
    else:
        file_metadata = {'name': MEMORY_FILE}
        service.files().create(body=file_metadata, media_body=media).execute()
    os.remove(MEMORY_FILE)

# GOOGLE LOGIN BUTTON
if 'credentials' not in st.session_state:
    st.link_button("🔐 Connect Google Drive", "https://accounts.google.com")
    st.info("After connecting, come back and refresh the page")
else:
    memory = load_memory_from_drive()
    
    # SIDEBAR
    with st.sidebar:
        st.header("🧠 JARVIS BRAIN - Saved to Your Drive")
        memory["name"] = st.text_input("Name", memory["name"])
        memory["phone"] = st.text_input("Phone", memory["phone"])
        memory["email"] = st.text_input("Email", memory["email"])
        memory["exp"] = st.text_area("Experience", memory["exp"])
        memory["loc"] = st.text_input("Location", memory["loc"])
        
        if st.button("Save to Google Drive"):
            save_memory_to_drive(memory)
            st.success("Saved to YOUR Google Drive ✅")
        
        st.divider()
        st.subheader("📚 Learning History")
        for item in memory["history"][-5:]:
            st.caption(f"- {item}")

    # MAIN
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    prompt = st.text_area("Ask JARVIS:")
    
    if st.button("Ask JARVIS"):
        mem_context = f"User: {memory['name']} Phone:{memory['phone']} Exp:{memory['exp']} Location:{memory['loc']}"
        full_prompt = f"Use this info: {mem_context}\n\nRequest: {prompt}"
        
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role":"user","content":full_prompt}],
                max_tokens=1500
            )
            answer = response.choices[0].message.content
            st.write(answer)
            
            memory["history"].append(f"{datetime.now().strftime('%d/%m')}: {prompt[:50]}...")
            save_memory_to_drive(memory)
