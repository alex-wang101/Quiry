import os
import certifi
import numpy as np
import faiss
import google.generativeai as gen
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Ensure MongoDB and API keys are set
if not MONGO_URI:
    raise ValueError("MONGO_URI not found")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found")

# Connect to MongoDB Atlas
mongo_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)

# Configure Google Gemini API
gen.configure(api_key=GEMINI_API_KEY)

# Function to get the correct database
def get_server_db(server_id):
    return mongo_client[f"discord_server_{server_id}"]

# Function to generate text embeddings using Google Gemini
# Generates vector embeddings for a given text using Google Gemini API
def generate_embedding(text):
    response = gen.embed_content(
        # Make sure this is always text-embedding-004, embed_content only exists there
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document"
    )
    return response["embedding"]

# Stores a message with vector embeddings in MongoDB.
def store_message(server_id, author, user_id, content, category, channel, server):    
    # Ensure content is valid before generating embedding
    if not content.strip():  
        print("skipping message")
        return  

    embedding = generate_embedding(content)  #Generate vector embedding (as a list)

    db = get_server_db(server_id)
    collection = db["messages"]

    # Ensure message_data is properly formatted before inserting
    message_data = {
        "author": author,
        "user_id": user_id,
        "text_message": content,
        "embedding": embedding, # Embeddings stored here
        "timestamp": datetime.now(timezone.utc),
        "category": category or "No category",
        "channel": channel,
        "server": server
    }

    collection.insert_one(message_data)
