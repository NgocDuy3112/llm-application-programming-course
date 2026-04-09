import os
from openai import OpenAI
from dotenv import load_dotenv



load_dotenv()


groq_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)