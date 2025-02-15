import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import store_message, fetch_messages

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f' Logged in as {bot.user.name}')
    await bot.tree.sync()
    print(" Bot is running!")

@bot.event
async def on_message(message):
    # Stores every message in the correct individual servers database."
    if message.author == bot.user or not message.guild:
        return  

    store_message(
        server_id=message.guild.id,  
        author=str(message.author),
        user_id=message.author.id,
        content=message.content,
        channel=str(message.channel),
        server=str(message.guild.name)
    )

    await bot.process_commands(message) 

# fetches recent messages and searches for an answer."
@bot.tree.command(name="ask", description="Ask me anything about this server!")
async def ask(interaction: discord.Interaction, question: str):

    server_id = interaction.guild_id  
    messages = fetch_messages(server_id, limit=20) 

    # Simple keyword search (Replace with AI-based answer retrieval later)
    matches = [msg["content"] for msg in messages if question.lower() in msg["content"].lower()]
    response = matches[0] if matches else "I don't have an answer for that yet!"

    await interaction.response.send_message(response)
