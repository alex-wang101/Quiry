import os
import certifi
import numpy as np
import faiss
import google.generativeai as gen
from pymongo import MongoClient
from dotenv import load_dotenv
from math import sqrt
from database import get_server_db, generate_embedding

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

mongo_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)

# Configure Google Gemini API
gen.configure(api_key=GEMINI_API_KEY)

CHECK_COSINE_SIMILARITY = True


# Load embeddings from MongoDB and initializes FAISS searching
def load_embeddings(server_id):
    db = get_server_db(server_id)
    collection = db["messages"]

    # Retrieve all messages from the database, including only necessary fields
    cursor = collection.find(
        {},
        {
            "_id": 1,
            "embedding": 1,
            "text_message": 1
        }
    )
    all_messages = list(cursor)

    if not all_messages:
        return None, None, None

    # Build an array of embeddings
    embeddings = np.array([doc["embedding"] for doc in all_messages], dtype=np.float32)
    message_text_mapping = {str(doc["_id"]): doc["text_message"] for doc in all_messages}

    # Build the FAISS index
    embedding_dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dimension)
    index.add(embeddings)

    return index, all_messages, message_text_mapping

# Uses FAISS to find vectors that are the most similar to eachother.
def search_similar_messages(query, index, all_docs, text_map, top_k=5):
    
    if index is None:
        return []

    # Embed the query using Gemini
    query_embedding = generate_embedding(query)
    query_embedding_np = np.array([query_embedding], dtype=np.float32)

    # FAISS the top_k most similar vectors
    distances, indices = index.search(query_embedding_np, top_k)

    candidates = []
    for index in indices[0]:
        if index < len(all_docs):
            doc = all_docs[index]
            candidates.append(doc)

    if not candidates:
        return []

    if CHECK_COSINE_SIMILARITY:
        # Rerank using cosine similarity
        query_norm = sqrt(sum(x*x for x in query_embedding))

        def cosine_sim(query_vec, doc_vec):
            dot_val = sum(q*d for q, d in zip(query_vec, doc_vec))
            doc_norm = sqrt(sum(d*d for d in doc_vec))
            #print(dot_val / (query_norm * doc_norm + 1e-9)
            return dot_val / (query_norm * doc_norm + 1e-9)

        scored_candidates = []
        for c in candidates:
            doc_embedding = c["embedding"]
            score = cosine_sim(query_embedding, doc_embedding)
            scored_candidates.append((c, score))

        # Sort by descending similarity
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Extract top_k text
        top_texts = []
        for cand_doc, _ in scored_candidates[:top_k]:
            msg_id = str(cand_doc["_id"])
            top_texts.append(text_map[msg_id])
        return top_texts
    else:
        # No cosine similarity, then just approximate order from FAISS
        top_texts = []
        for doc in candidates:
            msg_id = str(doc["_id"])
            top_texts.append(text_map[msg_id])
        return top_texts


# Generates response using Gemini Pro
def generate_response(query, server_id, top_k=5):
    # Load existing embeddings into FAISS
    index, all_docs, text_map = load_embeddings(server_id)
    if index is None:
        return "No relevant messages have been indexed for this server yet."

    # Get the top_k chunks
    relevant_chunks = search_similar_messages(query, index, all_docs, text_map, top_k=top_k)
    
    #print(relevant_chunks)
    if not relevant_chunks:
        context = "No similar messages were found in the database."
    else:
        context = "\n".join(relevant_chunks)

    prompt = f"""You are a helpful, factual AI that is given a conversation log (context) and a user query. Your task is to find the answer to the query using the provided context. Follow these rules:

1. If the answer is clearly present in the context, provide a direct answer using the context. For example, if the user asks, "Who's mom bakes like a champion?" and the context includes a message where a user "pppravin" states, "my mom bakes like a champion," your answer should be "pppravin's mom bakes like a champion."
2. If the context is unclear or does not contain the information required to answer the query, reply with: "I’m sorry, I cannot find that information."
3. For any additional details requested by the user, provide a direct, concise answer based solely on the context.
4. If the context includes flagged content (e.g., hate speech, harassment, or similar issues) that prevents you from generating a safe response, indicate which message is causing the error.
5. When outputing a timestamp, only say the date not the hours, and output a reasonable estimation for the amount of time that has passed since the message.

Context:
{context}

User query: {query}

"""
    model = gen.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    return response.text
