import streamlit as st
import asyncio
from unified import UnifiedApis
import time

# Define available models for OpenRouter
models = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "openai/gpt-4o-2024-08-06",
    "openai/o1-mini",
    "anthropic/claude-3.5-sonnet:beta",
    "google/gemini-pro"
]

st.title("Multi-Model Chat App")

# Function to check if the API key is valid and not expired
def is_api_key_valid():
    return (
        "api_key" in st.session_state
        and "api_key_expiry" in st.session_state
        and st.session_state.api_key_expiry > time.time()
    )

# API Key input in sidebar
with st.sidebar:
    st.header("API Key Configuration")
    if not is_api_key_valid():
        api_key = st.text_input("Enter your OpenRouter API Key", type="password")
        if st.button("Save API Key"):
            st.session_state.api_key = api_key
            st.session_state.api_key_expiry = time.time() + 12 * 3600  # 12 hours from now
            st.success("API Key saved for 12 hours!")
    else:
        st.success("API Key is valid.")
        if st.button("Clear API Key"):
            del st.session_state.api_key
            del st.session_state.api_key_expiry
            st.experimental_rerun()

    # Model selection
    selected_model = st.selectbox("Choose a model", models)

# Main chat interface
if is_api_key_valid():
    # Initialize the UnifiedApis with the selected model
    chat = UnifiedApis(name="Streamlit Multi-Model Chat App", use_async=True, model=selected_model, api_key=st.session_state.api_key)

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

else:
    st.warning("Please enter your OpenRouter API Key in the sidebar to start chatting.")