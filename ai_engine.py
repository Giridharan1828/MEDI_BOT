import streamlit as st
from groq import Groq

# This pulls the key from your Streamlit Secrets (cloud) 
# or .streamlit/secrets.toml (local)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def call_medibot(messages):
    """
    Sends a list of messages to the Groq Llama 3 model 
    and returns the AI's text response.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error connecting to AI Engine: {str(e)}"