import os
import openai
import streamlit as st
from dotenv import load_dotenv

# Set dark mode and layout
st.set_page_config(
    page_title="Multi-Model Chat",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main container */
    .stApp {
        margin: 0 auto;
        padding: 2rem;
        width: 100%;
        overflow: visible;
    }
    
    /* Remove internal scrollbars */
    .main .block-container {
        overflow: visible;
    }
    
    /* Adjust chat container */
    .stChatMessage {
        max-width: 100%;
        margin: 0.5rem 0;
    }
    
    /* Chat messages */
    .stChatMessage {
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* User message */
    .stChatMessage[data-testid="user"] {
        background-color: #3b82f6;
        color: white;
    }
    
    /* Assistant message */
    .stChatMessage[data-testid="assistant"] {
        background-color: #374151;
        color: white;
    }
    
    /* Input area */
    .stTextArea textarea {
        border-radius: 12px;
        padding: 1rem;
        
    }
    
    /* Send button */
    .stButton button {
        border-radius: 12px;
        background-color: #ef8e78;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    
    /* Model selection */
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 12px;
        background-color: #1f2937;
    }
    
    /* Table styling */
    table {
        width: 100%;
        border: none;
        margin: 1rem 0;
        border: none;
    }
    
    th, td {
        padding: 0.75rem;
        text-align: left;
        border: none;
    }
    
    th {
        background-color: #ef8e78;
        color: white;
    }
    
    tr:nth-child(even) {
        background-color: #eeeeee;
    }
    
    tr:nth-child(odd) {
        background-color: #ffffff;
    }
    
    tr:hover {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# If there's no API key, throw an error.
if not OPENROUTER_API_KEY:
    st.error("OpenRouter API key not found. Please set OPENROUTER_API_KEY in your .env file.")
    st.stop()

# Initialize OpenAI client with OpenRouter configuration
client = openai.OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Dictionary of models with simple names
MODEL_OPTIONS = {
    "deepseek/deepseek-chat": "Deepseek",
    "anthropic/claude-3.5-sonnet:beta": "Claude 3.5",
    "openai/o1": "o1",
    "openai/gpt-4o-2024-11-20": "4o",
    "google/gemini-2.0-flash-exp:free": "Gemini 2.0",
    "perplexity/llama-3.1-sonar-huge-128k-online": "Perplexity Sonar"
}

# Helper function to send messages to OpenRouter
def get_openrouter_response(messages, model):
    """
    messages: a list of dict -> [{"role": "system", "content": ...}, {"role": "user", "content": ...}]
    model: str -> the model ID to be used (e.g. "anthropic/claude-3.5-sonnet:beta")
    Returns a string -> the assistant's response
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
            extra_headers={
                "HTTP-Referer": "https://github.com/maliwansavage/model-choice",
                "X-Title": "Streamlit Multi-Model Chat",
            }
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI setup
st.title("Multi-Model Chat")

# Model selection radio buttons
selected_model_key = st.radio(
    "Choose your model:",
    list(MODEL_OPTIONS.keys()),
    format_func=lambda x: MODEL_OPTIONS[x],
    label_visibility="collapsed",
    horizontal=True
)

# Model selection table
model_table = """
| Model | Good at | Cost |
|-------|---------|------|
| Deepseek | Logical thinking | Very Low |
| Claude 3.5 | Clever reasoning | Medium |
| o1 | Complex problem solving | High |
| 4o | Creative writing | Low |
| Gemini 2.0 | General reasoning | Free |
| Perplexity Sonar | Up-to-date info | Low |
"""
st.markdown(model_table)

# Initialize conversation in session state
if "conversation" not in st.session_state:
    st.session_state.conversation = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Create containers for chat display and input
chat_container = st.container()
input_container = st.container()

# Chat input at bottom
with input_container:
    with st.form("chat_form", clear_on_submit=True):
        cols = st.columns([0.85, 0.15])
        with cols[0]:
            user_input = st.text_area(
                "Type your message...",
                key="user_input",
                height=100,
                label_visibility="collapsed"
            )
        with cols[1]:
            submit_button = st.form_submit_button("Send", use_container_width=True)
        
        if user_input.strip():
            # Add user message to conversation
            st.session_state.conversation.append({"role": "user", "content": user_input})
            
            # Call helper function to get the model response
            model_response = get_openrouter_response(st.session_state.conversation, selected_model_key)
            
            # Add assistant response to conversation
            st.session_state.conversation.append({"role": "assistant", "content": model_response})

# Display messages above input
with chat_container:
    for msg in st.session_state.conversation:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])
