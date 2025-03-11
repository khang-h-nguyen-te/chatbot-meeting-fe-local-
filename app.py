import streamlit as st
import requests
from dotenv import load_dotenv
import os

# -------------------------------
#        API CONFIGURATION
# -------------------------------
# Get environment variables
load_dotenv()
AUTH_COMMAND = os.getenv("AUTH_COMMAND")
BASE_URL = os.getenv("BASE_URL")

# Construct URLs
LOGIN_API_URL = f"{BASE_URL}/authenticate/{AUTH_COMMAND}"
CHAT_API_URL = f"{BASE_URL}/ask"

# -------------------------------
# Initialize session state variables if not already set
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# We’ll store messages as a list of dicts, e.g.:
# {"role": "user", "content": "..."} or {"role": "assistant", "content": "..."}
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar: Login Form ---
st.sidebar.header("User Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Sign In"):
    # Create payload for login
    payload = {"email": username, "password": password}
    try:
        response = requests.post(LOGIN_API_URL, json=payload)
        if response.status_code == 200:
            st.session_state.authenticated = True
            st.sidebar.success("Logged in successfully!")
        else:
            st.sidebar.error("Invalid credentials. Please try again.")
    except Exception as e:
        st.sidebar.error("Error connecting to the login API.")

# --- Main Page: Chatbot Interface ---
if st.session_state.authenticated:
    st.title("Virtual Assistant")

    # 1) Display existing chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 2) Chat input box (new in Streamlit)
    user_input = st.chat_input("Type your message here...")
    if user_input:
        # -- USER MESSAGE --
        # Append to session state
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Display it immediately
        with st.chat_message("user"):
            st.write(user_input)

        # -- CALL CHATBOT API --
        payload = {"query": user_input}  # Adjust to match your API's payload
        try:

            chat_response = requests.post(CHAT_API_URL, json=payload)
            if chat_response.status_code == 200:
                data = chat_response.json()
                bot_reply = data["response"].get("response", "No reply received.")
            else:
                bot_reply = f"Error: Chatbot API call failed (status {chat_response.status_code})."
        except Exception as e:
            bot_reply = f"Error: Could not connect to the chatbot API. Details: {e}"

        # -- ASSISTANT MESSAGE --
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            # loading_placeholder.empty()  # Remove loading message
            st.write(bot_reply)
else:
    st.write("Please sign in using the sidebar to access the chatbot.")

