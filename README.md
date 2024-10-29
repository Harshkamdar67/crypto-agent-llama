# Crypto Agent Assignment - Documentation

## Overview

This project is an AI agent built for the Sarvam.ai assignment. It integrates the Together AI API and an external cryptocurrency pricing API to create an interactive conversational agent that can provide real-time crypto prices and handle language translation requests, while maintaining a consistent communication flow in English.

The core functionalities of this project include:

1. Fetching current cryptocurrency prices using the CoinGecko API.
2. Handling rate limiting and caching for efficient API usage.
3. Maintaining conversational context to ensure smooth interaction.
4. Using prompt engineering techniques to classify user intents effectively.
5. Allowing the user to switch languages, while ensuring responses remain in English.

## Features

- **Real-time Cryptocurrency Prices**: The agent fetches the current price of specified cryptocurrencies.
- **Language Change Requests**: Handles language change requests from users, while maintaining English as the primary response language.
- **Rate Limiting and Caching**: Limits the number of API calls within a given time frame and uses caching to store recent responses.
- **Intent Classification**: Classifies user intents into `crypto`, `general`, or `language_change` using a large language model (LLaMA 3.1 8B).

## Technologies Used

- **Python**: The primary programming language used for the implementation.
- **Together AI API**: For LLaMA 3.1 8B model to perform intent classification and generate conversational responses.
- **CoinGecko API**: For retrieving real-time cryptocurrency prices.
- **dotenv**: For managing environment variables.
- **Regex**: For extracting structured JSON responses from the model output.

## Requirements

- Python 3.9+
- Environment variables managed via `.env` file (API key)
- Libraries listed in `requirements.txt`

## Setup Instructions

1. **Clone the Repository**:

   ```sh
   git clone https://github.com/Harshkamdar67/SarvamAI-cryptoagent-assignment.git
   cd <repository-folder>
   ```
2. **Create a Virtual Environment**:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. **Install Dependencies**:

   ```sh
   pip install -r requirements.txt
   ```
4. **Create a ****************`.env`**************** File**: Create a `.env` file in the root directory and add the necessary API keys and configurations, for example:

   ```env
   TOGETHER_API_KEY=your_together_api_key
   ```
5. **Run the Agent**:

   ```sh
   python main.py
   ```

## Example Usage

To start a conversation with the Crypto Agent, simply run the script using `python main.py`. You can then type in requests, such as:

- "What's the price of Bitcoin?"
- "Can you switch to French?"

The agent will maintain context and respond in a friendly manner.

## Prompt Engineering Approach

- **Role Assignment**: The model is instructed to act as an assistant capable of classifying user intents clearly.
- **Contextual Clarity**: Each prompt is designed to explicitly ask the model to provide output in a specific JSON format, ensuring easy parsing.
- **Triple Backticks and Regex**: The JSON response is wrapped in triple backticks to facilitate structured extraction using regular expressions, minimizing parsing errors.

## Example Conversation

```
You: hey whats up

Assistant: Not much, just here to help with any questions or topics you'd like to discuss. How's your day going so far?

You: price of bitcoin?

Assistant: The current price of bitcoin is $71157 USD.

You: should i buy it?

Assistant: I can't give you financial advice. However, I can provide some general information about bitcoin. Would that help?

You: sure

Assistant: Here are some general points to consider:

1. **Volatility**: Bitcoin is known for its high price volatility, which means its value can fluctuate rapidly and unpredictably. This can be both a risk and an opportunity.
2. **Investment risk**: Bitcoin is a high-risk investment, and its value can drop significantly in a short period. If you're not comfortable with the possibility of losing some or all of your investment, it may not be the right choice for you.
3. **Lack of regulation**: Bitcoin is not regulated by any government or institution, which can make it difficult to understand and navigate.
4. **Security risks**: Bitcoin exchanges and wallets can be vulnerable to hacking and other security threats, which can result in the loss of your funds.
5. **Liquidity**: Bitcoin is a relatively small market compared to traditional assets like stocks or bonds, which can make it difficult to buy or sell large amounts quickly.
6. **Long-term potential**: Some people believe that bitcoin has long-term potential as a store of value and a form of payment, but this is still a speculative area.

If you're still interested in investing in bitcoin, consider the following:

1. **Educate yourself**: Learn as much as you can about bitcoin, its technology, and its potential uses.
2. **Set a budget**: Decide how much you're willing to invest and stick to it.
3. **Diversify**: Consider investing in a diversified portfolio of assets to minimize risk.
4. **Consult a financial advisor**: If you're unsure about investing in bitcoin, consider consulting a financial advisor who can provide personalized advice.

Remember, investing in bitcoin is a personal decision that should be based on your individual financial goals, risk tolerance, and circumstances.

Would you like to know more about any of these points?

You: actually i would like to speak in hindi

Assistant: I have noted your language change request. You can continue using the new language, but I will respond in English to ensure consistency and clarity.

You: एथेरियम की कीमत क्या है

Assistant: The current price of ethereum is $2619.78 USD.

You: thanks!

```

## Assumptions and Limitations

- **Language Consistency**: While the user can change their input language, all responses from the agent will remain in English to ensure clear communication.
- **Rate Limiting**: The rate limiter is set to allow 5 API requests per minute, which may limit functionality during high-volume queries.
- **Limited Languages**: The language change feature does not perform actual translations; it acknowledges the user's request but maintains English responses.
