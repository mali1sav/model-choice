# Multi-Model Chat Application

A modern Streamlit-based chat application with advanced UI and multiple LLM model support.

## Features
- Modern UI with dark mode and responsive design
- Horizontal radio button model selection
- Clean table view of model capabilities
- Asynchronous API calls with retry logic
- Chat history management
- Environment variable configuration
- Browser-native scrolling

## Available Models
| Model | Strengths | Cost |
|-------|-----------|------|
| Claude 3.5 | Advanced reasoning, creative tasks | Medium |
| O1 | Complex problem solving, technical queries | High |
| Deepseek | Logical thinking, cost-effective | Very Low |
| 4o | Creative writing, storytelling | Low |
| Gemini 2.0 | General knowledge, basic queries | Free |
| Sonar | Real-time information, web access | Low |

## Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```
4. Run the application:
   ```bash
   streamlit run main.py
   ```

## Usage
1. Select your preferred model using the radio buttons
2. Review model capabilities in the table
3. Type your message in the chat input
4. View the model's response in the chat window

## Requirements
- Python 3.8+
- Streamlit
- OpenAI Python client
