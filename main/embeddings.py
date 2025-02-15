import os
from dotenv import load_dotenv
import google.generativeai as genai
import numpy as np
import faiss 
from pymongo import MongoClient


# Load from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check for possible error source
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing")

client = MongoClient("MONGO_URI")
db = client["DiscordBotDB"]
collection = db["messages"]




