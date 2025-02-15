import os
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Check for possible error source
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file! Please check your environment variables.")

# Connect to MongoDB Atlas (Ensure it's NOT localhost)
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) 
    mongo_client.admin.command("ping") 
    print("Successfully connected to MongoDB Atlas")
except errors.ServerSelectionTimeoutError as e:
    raise RuntimeError(f"MongoDB Atlas Connection Error: {e}")

# Returns the MongoDB database for a specific Discord server
def get_server_db(server_id):
    return mongo_client[f"discord_server_{server_id}"]

# Stores a message in the server-specific database.
def store_message(server_id, author, user_id, content, category, channel, server):
    db = mongo_client[f"discord_server_{server_id}"]
    collection = db["messages"]

    message_data = {
        "author": author,
        "user_id": user_id,
        "text_message": content,
        "timestamp": datetime.now(timezone.utc),
        "category": category,  
        "channel": channel,
        "server": server
    }

    try:
        print(f"Storing in Database: {db.name}, Collection: messages")  
        collection.insert_one(message_data)
        print(f"Saved message in {db.name}: {content} (Category: {category})")
    except Exception as e:
        print(f"Error storing message in MongoDB: {e}")
        
# Fetches the last N messages from the server's database."""
def fetch_messages(server_id, limit=10):
    db = get_server_db(server_id)
    try:
        return list(db["messages"].find().sort("timestamp", -1).limit(limit))
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []
