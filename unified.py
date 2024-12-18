import os
import json
import openai
from termcolor import colored
import time
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class UnifiedApis:
    def __init__(self,
                 name="Unified Apis",
                 api_key=None,
                 max_history_words=20000,
                 max_words_per_message=None,
                 json_mode=False,
                 stream=True,
                 use_async=False,
                 max_retry=10,
                 model="openai/gpt-3.5-turbo",
                 should_print_init=True,
                 print_color="green"
                 ):
        
        self.model = model
        self.name = name
        self.api_key = api_key or self._get_api_key()
        self.history = []
        self.max_history_words = max_history_words
        self.max_words_per_message = max_words_per_message
        self.json_mode = json_mode
        self.stream = stream
        self.use_async = use_async
        self.max_retry = max_retry
        self.print_color = print_color
        self.system_message = "You are a helpful assistant."
        if self.json_mode:
            self.system_message += " Please return your response in JSON format unless specified otherwise."

        self._initialize_client()

        if should_print_init:
            print(colored(f"{self.name} initialized with model={self.model}, json_mode={json_mode}, stream={stream}, use_async={use_async}, max_history_words={max_history_words}, max_words_per_message={max_words_per_message}", "red"))

    def _get_api_key(self):
        return os.getenv("OPENROUTER_API_KEY")

    def _initialize_client(self):
        if not self.api_key:
            raise ValueError("API key for OpenRouter is not set in the .env file")
        # No need to initialize a separate client; openai library handles it.

    def set_system_message(self, message=None):
        self.system_message = message or "You are a helpful assistant."
        if self.json_mode and "json" not in message.lower():
            self.system_message += " Please return your response in JSON format unless specified otherwise."

    async def set_system_message_async(self, message=None):
        self.set_system_message(message)

    def add_message(self, role, content):
        if role == "user" and self.max_words_per_message:
            content += f" please use {self.max_words_per_message} words or less"
        self.history.append({"role": role, "content": str(content)})

    async def add_message_async(self, role, content):
        self.add_message(role, content)

    def print_history_length(self):
        history_length = sum(len(str(message["content"]).split()) for message in self.history)
        print(f"\nCurrent history length is {history_length} words")

    async def print_history_length_async(self):
        self.print_history_length()

    def clear_history(self):
        self.history.clear()

    async def clear_history_async(self):
        self.clear_history()

    def chat(self, user_input, **kwargs):
        self.add_message("user", user_input)
        return self.get_response(**kwargs)

    async def chat_async(self, user_input, **kwargs):
        await self.add_message_async("user", user_input)
        return await self.get_response_async(**kwargs)

    def trim_history(self):
        words_count = sum(len(str(message["content"]).split()) for message in self.history if message["role"] != "system")
        while words_count > self.max_history_words and len(self.history) > 1:
            words_count -= len(self.history[0]["content"].split())
            self.history.pop(0)

    async def trim_history_async(self):
        self.trim_history()

    def get_response(self, color=None, should_print=True, **kwargs):
        if color is None:
            color = self.print_color
        
        max_tokens = kwargs.pop('max_tokens', 5000)

        retries = 0
        while retries < self.max_retry:
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "system", "content": self.system_message}] + self.history,
                    stream=self.stream,
                    max_tokens=max_tokens,
                    **kwargs
                )
                
                if self.stream:
                    assistant_response = ""
                    for chunk in response:
                        if 'choices' in chunk and 'delta' in chunk['choices'][0] and 'content' in chunk['choices'][0]['delta']:
                            content = chunk['choices'][0]['delta']['content']
                            if should_print:
                                print(colored(content, color), end="", flush=True)
                            assistant_response += content
                    print()
                else:
                    assistant_response = response.choices[0].message.content

                if self.json_mode:
                    try:
                        assistant_response = json.loads(assistant_response)
                    except json.JSONDecodeError:
                        print("Warning: Response is not in valid JSON format. Returning as string.")

                self.add_message("assistant", str(assistant_response))
                self.trim_history()
                return assistant_response
            except Exception as e:
                print("Error:", e)
                retries += 1
                time.sleep(1)
        raise Exception("Max retries reached")

    async def get_response_async(self, color=None, should_print=True, **kwargs):
        if color is None:
            color = self.print_color
        
        max_tokens = kwargs.pop('max_tokens', 4000)
        
        retries = 0
        while retries < self.max_retry:
            try:
                response = await openai.ChatCompletion.acreate(
                    model=self.model,
                    messages=[{"role": "system", "content": self.system_message}] + self.history,
                    stream=self.stream,
                    max_tokens=max_tokens,
                    **kwargs
                )

                if self.stream:
                    assistant_response = ""
                    async for chunk in response:
                        if 'choices' in chunk and 'delta' in chunk['choices'][0] and 'content' in chunk['choices'][0]['delta']:
                            content = chunk['choices'][0]['delta']['content']
                            if content:
                                if should_print:
                                    print(colored(content, color), end="", flush=True)
                                assistant_response += content
                    print()
                else:
                    assistant_response = response.choices[0].message.content

                if self.json_mode:
                    try:
                        assistant_response = json.loads(assistant_response)
                    except json.JSONDecodeError:
                        print("Warning: Response is not in valid JSON format. Returning as string.")

                await self.add_message_async("assistant", str(assistant_response))
                await self.trim_history_async()
                return assistant_response
            except Exception as e:
                print("Error:", e)
                retries += 1
                await asyncio.sleep(1)
        raise Exception("Max retries reached")
        