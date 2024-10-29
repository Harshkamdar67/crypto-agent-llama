from together import Together
from dotenv import load_dotenv
import os
import requests
import json
import time
from typing import Dict, Union
import re

class CryptoAgent:
    def __init__(self):
        """Initialize the agent, load environment variables, and set up Together client."""
        load_dotenv()
        self.client = Together()
        self.context = []
        self.cache = {}  # Cache for storing recent API responses
        self.rate_limit_window = 60  # Rate limit window in seconds
        self.rate_limit_max_requests = 5  # Max requests per window
        self.request_timestamps = []  # List of request timestamps for rate limiting
    
    def add_message_to_context(self, role: str, content: str) -> None:
        """Store a message in the conversation context."""
        self.context.append({"role": role, "content": content})
    
    def is_rate_limited(self) -> bool:
        """Check if API calls are rate-limited based on request timestamps."""
        current_time = time.time()
        
        # Remove timestamps older than the rate limit window
        self.request_timestamps = [t for t in self.request_timestamps if current_time - t < self.rate_limit_window]
        
        # Check if within the rate limit
        if len(self.request_timestamps) >= self.rate_limit_max_requests:
            return True
        else:
            self.request_timestamps.append(current_time)
            return False

    def get_crypto_price(self, crypto_symbol: str) -> str:
        """Fetch the current price of the specified cryptocurrency with caching and rate limiting."""
        
        # Rate limit check
        if self.is_rate_limited():
            return "Rate limit exceeded. Please wait a moment before trying again."
        
        # Check cache for recent data
        current_time = time.time()
        cache_entry = self.cache.get(crypto_symbol)
        
        # Use cached data if it's recent (cache duration: 60 seconds)
        if cache_entry and (current_time - cache_entry['timestamp'] < 60):
            print("Using cached data.")
            return cache_entry['price']
        
        # Otherwise, make the API call
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': crypto_symbol,
            'vs_currencies': 'usd'
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Check for request errors
            data = response.json()
            price = data.get(crypto_symbol, {}).get('usd')
            if price:
                # Store the result in cache
                self.cache[crypto_symbol] = {'price': f"The current price of {crypto_symbol} is ${price} USD.", 'timestamp': current_time}
                return self.cache[crypto_symbol]['price']
            else:
                return "Price not available."
        except requests.RequestException as e:
            print(f"Error fetching crypto price: {e}")
            return "Failed to fetch price."

    def classify_intent(self, user_message: str) -> Dict[str, Union[str, None]]:
        """Use LLM to classify the user's query as 'crypto', 'general', or 'language_change'."""
        
        intent_prompt = [
            {"role": "system", "content": "You are an AI assistant that helps classify user intents accurately to ensure smooth conversation flow."},
            {"role": "user", "content": f"Classify this query: '{user_message}'. Reply with a JSON object containing 'intent' as either 'crypto', 'general', or 'language_change'. Wrap the JSON response within triple backticks (```json ... ```). Make sure to provide a clear and definitive answer."}
        ]

        try:
            response = self.client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                messages=intent_prompt
            )
            response_text = response.choices[0].message.content
            # Extract JSON wrapped in triple backticks using regex
            json_match = re.search(r'```json\n(\{.*?\})\n```', response_text, re.DOTALL)
            if json_match:
                intent_data = json.loads(json_match.group(1))
                intent = intent_data.get("intent")
                return {"intent": intent}
            else:
                print("Error: Failed to extract JSON from LLM response.")
                return {"intent": "general"}
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            print(f"Error: Failed to parse LLM response for intent classification. {e}")
            return {"intent": "general"}
        except Exception as e:
            print(f"Unexpected error during intent classification: {e}")
            return {"intent": "general"}

    def process_user_message(self, user_message: str) -> None:
        """Process a user message, classify it, and generate a response accordingly."""
        self.add_message_to_context("user", user_message)
        
        # Get the intent classification
        classification = self.classify_intent(user_message)
        intent = classification.get("intent", "general")

        if intent == "crypto":
            self.process_crypto_query(user_message)
        elif intent == "language_change":
            self.process_language_change(user_message)
        else:
            self.process_general_query()

    def process_crypto_query(self, user_message: str) -> None:
        """Process cryptocurrency-related queries by using the price fetching tool."""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_crypto_price",
                    "description": "Fetches the current price of a specified cryptocurrency in USD",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "crypto_symbol": {
                                "type": "string",
                                "description": "The cryptocurrency name, e.g., ethereum",
                            }
                        },
                        "required": ["crypto_symbol"]
                    }
                }
            }
        ]
        
        # Add assistant intro message if it’s the first message in context
        if not any(msg["role"] == "assistant" for msg in self.context):
            self.add_message_to_context(
                "assistant",
                "Hello! You are interacting with a cryptocurrency expert. I can provide real-time crypto prices and answer related questions. If you misspell a crypto name, I will correct it for you."
            )
        
        try:
            # Make the Together AI API call with tool support
            response = self.client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                messages=self.context,
                tools=tools,
                tool_choice="auto",
            )

            tool_calls = response.choices[0].message.tool_calls
            if tool_calls:
                for tool_call in tool_calls:
                    if tool_call.function.name == "get_crypto_price":
                        arguments = json.loads(tool_call.function.arguments)
                        crypto_symbol = arguments['crypto_symbol']
                        price_info = self.get_crypto_price(crypto_symbol)
                        self.add_message_to_context("assistant", price_info)
                        print(f"Assistant: {price_info}")
            else:
                response_text = response.choices[0].message.content
                self.add_message_to_context("assistant", response_text)
                print(f"Assistant: {response_text}")
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            print(f"Error processing crypto query: {e}")
        except Exception as e:
            print(f"Unexpected error during crypto query processing: {e}")

    def process_language_change(self, user_message: str) -> None:
        """Handle language change requests by confirming the new language while keeping system responses in English."""
        # Acknowledge the language change request but maintain system responses in English
        response_text = "I have noted your language change request. You can continue using the new language, but I will respond in English to ensure consistency and clarity."
        self.add_message_to_context("assistant", response_text)
        print(f"Assistant: {response_text}")

    def process_general_query(self) -> None:
        """Handle general queries that are not related to cryptocurrency."""
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                messages=self.context
            )
            response_text = response.choices[0].message.content
            self.add_message_to_context("assistant", response_text)
            print(f"Assistant: {response_text}")
        except (AttributeError, KeyError) as e:
            print(f"Error processing general query: {e}")
        except Exception as e:
            print(f"Unexpected error during general query processing: {e}")

    def start_conversation(self) -> None:
        """Start a conversation with the user."""
        print("Crypto Agent: Hello! I can help you check cryptocurrency prices or answer general questions.")
        print("Type 'exit' to end the conversation.\n")

        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() == "exit":
                    print("Crypto Agent: Goodbye!")
                    break
                self.process_user_message(user_input)
            except KeyboardInterrupt:
                print("\nCrypto Agent: Goodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")


if __name__ == "__main__":
    agent = CryptoAgent()
    agent.start_conversation()
