# Quiry: A Context-Aware Discord Bot

Quiry is a context-aware Discord bot that transforms your server's conversations into a searchable collective memory. Built with Python, discord.py, MongoDB Atlas, FAISS, and the Google Generative AI (Gemini API), Quiry leverages high-dimensional vector embeddings to enable Retrieval-Augmented Generation (RAG) for dynamic, context-driven responses.

---

## Features

- **Semantic Search**  
  Quickly retrieve contextually similar messages from any channel, turning everyday chatter into actionable information.

- **Retrieval-Augmented Generation (RAG)**  
  Dynamically generate answers by referencing the nearest past messages, enabling intelligent and context-aware responses.

- **Scalable Storage**  
  Manages hundreds of thousands of messages across multiple servers using **MongoDB Atlas** for reliable data storage.

- **Efficient Indexing**  
  **FAISS** provides near-instant similarity search, ensuring fast performance even under heavy message loads.

- **User-Friendly**  
  No complex setup required—just invite Quiry to your server, and it automatically indexes your conversations.

---

## Adding Quiry to Your Server

**[Invite Quiry](https://discord.com/oauth2/authorize?client_id=1340139928994189322&permissions=8&integration_type=0&scope=bot)**

1. Click the link above.  
2. Select the Discord server you want to add Quiry to.  
3. Grant the necessary permissions (e.g., reading message history).  
4. Quiry will join your server and begin indexing messages automatically.

---

## Usage

1. **Monitor and Store Messages**  
   - Quiry listens for new messages, converts them into vector embeddings (via the Gemini API), and stores them in MongoDB Atlas.
2. **Ask Questions**  
   - Use the `/ask` command to retrieve contextually similar past conversations. Quiry’s advanced RAG system provides intelligent responses based on your server’s history.
3. **Admin Commands** (optional)  
   - **`/clear X`** – Remove the most recent X messages from your server’s database (useful for data reset or privacy).  
   - **`/fetch X`** – (Currently Disabled) Backfill up to X historical messages from your server’s channels, giving Quiry a larger data set for retrieval.

---

## Technical Overview

- **Language & Libraries**  
  - Python, discord.py  
  - MongoDB Atlas (pymongo)  
  - NumPy, FAISS  
  - Google Generative AI (Gemini API)  
- **Core Concepts**  
  - **Vector Embeddings** for chat messages  
  - **Semantic Similarity Search** using FAISS  
  - **Retrieval-Augmented Generation (RAG)** for context-aware answers  
- **Architecture**  
  1. **Message Logging**: Listens to messages in real time.  
  2. **Embedding Generation**: Gemini API transforms each message into a high-dimensional vector.  
  3. **Indexing & Storage**: Embeddings stored in MongoDB Atlas and indexed with FAISS.  
  4. **Response Generation**: When asked, Quiry fetches the most similar embeddings, forms a context, and produces a relevant response.

---

## Disclaimer

- By adding Quiry to your server, you grant permission for message data to be stored and processed for semantic retrieval and context-aware responses.

---

## Contact & Support

If you have questions or need support, you can contact the bot’s owners:

- **Discord**: `[pppravin]`, `[alexwang06]`
- **Email**: `[pravin.lohani23@gmail.com]`, `[wangalex0140@gmail.com]`

Quiry is continually evolving to offer better search and AI-driven insights for your community. Feedback and suggestions are always welcome!
