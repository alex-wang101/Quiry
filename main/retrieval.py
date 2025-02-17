import os
import certifi
import numpy as np
import faiss
import google.generativeai as gen
from pymongo import MongoClient
from dotenv import load_dotenv
from database import generate_embedding, get_server_db

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

mongo_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)

# Configure Google Gemini API
gen.configure(api_key=GEMINI_API_KEY)

# Retrieves stored message embeddings from MongoDB and initializes a FAISS index to enable semantic search
def load_embeddings(server_id):
    db = get_server_db(server_id)
    collection = db["messages"]

    # Retrieve all messages from the database, including only necessary fields
    all_messages = []
    cursor = collection.find(
        {}, 
        {
            "_id": 1,
            "embedding": 1, 
            "text_message": 1
        }
    )

    # Iterate over the cursor and append each document to the list
    for document in cursor:
        all_messages.append(document)

    # If no messages are found in the database, return None to indicate an empty index
    if not all_messages:
        print("Sorry, no messages were found in the database for this server.")
        return None, None, None

    # Map vector embedding to strings
    embeddings = np.array([message["embedding"] for message in all_messages], dtype=np.float32)
    message_text_mapping = {str(message["_id"]): message["text_message"] for message in all_messages}
    embedding_dimension = embeddings.shape[1]

    # Search using Euclidean distance of the vectors in the 768th dimension
    index = faiss.IndexFlatL2(embedding_dimension)
    index.add(embeddings)

    return index, all_messages, message_text_mapping


# Searches for the most relevant messages in the FAISS index based on semantic similarity
def search_similar_messages(query, index, messages, message_texts, top_k=5):
    if index is None:
        return []

    # Generate a vector embedding for the user's query
    query_embedding = generate_embedding(query)
    query_embedding = np.array([query_embedding], dtype=np.float32)
    distances, indices = index.search(query_embedding, top_k)

    # Loop through the indices of the nearest neighbors
    similar_messages = []
    for index_position in indices[0]:
        if index_position < len(messages):
            message_id = str(messages[index_position]["_id"])
            similar_messages.append(message_texts[message_id])

    return similar_messages


#  Generates a response to a user query using past messages stored in the server's database
def generate_response(query, server_id):
    index, messages, message_texts = load_embeddings(server_id)
    if index is None:
        return "No relevant messages have been indexed for this server yet."
    
    relevant_messages = search_similar_messages(query, index, messages, message_texts)

    # If relevant messages are found, compile them into a response context
    if relevant_messages:
        context = "\n".join(relevant_messages)
    else:
        context = "No similar messages were found in the database."

    # Generate a response using Google Gemini AI
    model = gen.GenerativeModel("gemini-pro")
    response = model.generate_content(
        f"Based on past messages from this server, here is a response:\n\n{context}\n\nUser query: {query}"
    )

    return response.text
