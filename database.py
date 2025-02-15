import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

mongo_client = MongoClient(MONGO_URI)

def get_server_db(server_id):
    # Return the MongoDB database for a specific Discord server.
    return mongo_client[f"discord_server_{server_id}"]  

# Stores a message in the server-specific database.
def store_message(server_id, author, user_id, content, channel, server):

    db = get_server_db(server_id)
    collection = db["messages"]  
    
    message_data = {
        "author": author,
        "user_id": user_id,
        "content": content,
        "timestamp": datetime.now(timezone.utc),
        "channel": channel,
        "server": server
    }
    
    collection.insert_one(message_data)
    print(f" Saved message in server {server_id}: {content}")

# Gets the last N messages from the server's database 
def fetch_messages(server_id, limit=10):
    db = get_server_db(server_id)
    return list(db["messages"].find().sort("timestamp", -1).limit(limit))
