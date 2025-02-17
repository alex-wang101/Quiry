import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import store_message
from retrieval import generate_response

# Load environment variables (the hidden stuff)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Check for possible error source
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found")

# Enable intents
intents = discord.Intents.default()
intents.message_content = True

# Dictionary for spam detection
last_messages = {}

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()
    print("Bot is running!")


@bot.event
# Handles incoming messages, stores them in the mongodb database with category tracking
async def on_message(message):
    # Ignore messages from the bot itself or DMs to the bot
    if message.author == bot.user or not message.guild:
        return  

    # If the same user sends an identical message within 10 seconds then the message gets ignored
    current_time = message.created_at.timestamp()
    user_id = message.author.id
    if user_id in last_messages:
        last_content, last_time = last_messages[user_id]
        if message.content == last_content and (current_time - last_time) < 10:
            # print(f"Ignoring spam message from {message.author}")
            return
        
    # Update the last message record for the user
    last_messages[user_id] = (message.content, current_time)

    # Discord channels don't need to be in a category so make sure it is in one, otherwise no category
    if message.channel.category:
        category = message.channel.category.name
    else:
        category = "No Category"

    # Defining the paramters to store the dataset
    store_message(
        server_id=message.guild.id,  
        author=str(message.author),
        user_id=message.author.id,
        content=message.content,
        category=category,
        channel=str(message.channel),
        server=str(message.guild.name)
    )

    # Process commands
    await bot.process_commands(message)

# Fetches recent messages and searches for an answer.
@bot.tree.command(name="ask", description="Ask me anything about this server!")
async def ask(interaction: discord.Interaction, question: str):
    server_id = interaction.guild.id
    # Generate the response
    response = generate_response(question, server_id) 
    
    # Once the response is ready send a follow-up
    await interaction.response.send_message(response)


bot.run(TOKEN)