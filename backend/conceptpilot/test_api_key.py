# test_openai_key.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables from .env file (if you have OPENAI_API_KEY there)
load_dotenv()

# Get the API key from environment variables
groq_api_key = os.getenv('GROQ_API_KEY')

if not groq_api_key:
    print("Error: KEY environment variable not set.")
    print("Please set it in your .env file or directly in your environment.")
else:
    try:
        # Initialize the ChatOpenAI model
        llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.7, groq_api_key=groq_api_key)

        # Create a simple prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant."),
            ("user", "Say 'Hello, OpenAI!'")
        ])

        # Create a chain to invoke the LLM
        chain = prompt | llm | StrOutputParser()

        # Invoke the chain
        response = chain.invoke({})

        print("API Key Test Successful!")
        print(f"Response from groq: {response}")

    except Exception as e:
        print("API Key Test Failed!")
        print(f"Error: {e}")
        if "quota" in str(e).lower() or "billing" in str(e).lower():
            print("\nThis usually means you've exceeded your OpenAI quota or have a billing issue.")
            print("Please check your plan and billing details on platform.openai.com.")
        elif "authentication" in str(e).lower():
            print("\nThis usually means your API key is incorrect or revoked.")
            print("Please double-check your OPENAI_API_KEY.")