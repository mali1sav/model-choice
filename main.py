import streamlit as st
import asyncio
from unified import UnifiedApis
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for API key at startup
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("Please ensure OPENROUTER_API_KEY is set in your .env file")
    st.stop()

# Define available models for OpenRouter
models = [
    "openai/o1-mini",
    "openai/gpt-4o-2024-08-06",
    "meta-llama/llama-3.2-3b-instruct:free",
    "anthropic/claude-3.5-sonnet:beta",
    "google/gemini-pro"
]

st.title("Multi-Model Chat App")

# Model selection in sidebar
with st.sidebar:
    st.header("Model Selection")
    selected_model = st.selectbox("Choose a model", models)

# Initialize the UnifiedApis with the selected model
chat = UnifiedApis(
    name="Streamlit Multi-Model Chat App", 
    use_async=True, 
    model=selected_model, 
    api_key=OPENROUTER_API_KEY
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is your message?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = {"content": ""}
        
        # Generate response with asyncio and streamlit
        async def generate_response():
            response = await chat.chat_async(prompt, should_print=False)
            full_response["content"] = response
            message_placeholder.markdown(full_response["content"])
        
        asyncio.run(generate_response())
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response["content"]})

# Display the currently selected model
st.sidebar.write(f"Current model: {selected_model}")