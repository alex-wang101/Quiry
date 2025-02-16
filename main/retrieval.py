import os
import certifi
import numpy as np
import faiss
import google.generativeai as gen
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from database import generate_embedding


load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
mongo_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

gen.configure(api_key=GEMINI_API_KEY)

def retrieve_similar_messages(server_id, query_text, top_k=10):
    collection = mongo_client[f'discord_server_{server_id}']["messages"]
    query_embedding = generate_embedding(query_text).reshape(1, -1)
    messages = list(collection.find({}, {"_id": 1, "text_message": 1, "embedding": 1}))

    embeddings = np.array([msg["embedding"] for msg in messages], dtype=np.float32)

    #Initialize FAISS 
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    _, indicies = index.search(query_embedding, top_k)
    
    #Create a list of similar values
    similar = []
    for idx in indicies[0]:
        similar.append(messages[idx])
    
    return similar