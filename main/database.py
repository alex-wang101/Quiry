import os
import certifi
import google.generativeai as gen
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

""" 
# Checking if URI is valid 
if not MONGO_URI:
    raise ValueError("MONGO_URI not found")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found")
"""

mongo_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)

gen.configure(api_key=GEMINI_API_KEY)

# Retrieves to get the correct database
def get_server_db(server_id):
    return mongo_client[f"discord_server_{server_id}"]

# Function to generate text embeddings using Google Gemini
# Generates vector embeddings for a given text using Google Gemini API
def generate_embedding(text):
    response = gen.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document"
    )
    return response["embedding"]

# Stores a message with vector embeddings in MongoDB.
def store_message(server_id, author, user_id, content, category, channel, server):    
    if not content.strip():  
        #print("skipping message")
        return  

    embedding = generate_embedding(content)  

    db = get_server_db(server_id)
    collection = db["messages"]

    # Format the message before inserting into MongoDb
    message_data = {
        "author": author,
        "user_id": user_id,
        "text_message": content,
        "embedding": embedding, 
        "timestamp": datetime.now(ZoneInfo("America/Toronto")),
        "category": category or "No category",
        "channel": channel,
        "server": server
    }

    collection.insert_one(message_data)
