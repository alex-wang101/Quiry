import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Load environment variables (the token to keep it hidden)
load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

#Set up the bot with the necessary intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Successfully logged in as {bot.user.name}')
    await bot.tree.sync()  # Sync commands on startup
    print("slash commands synced")

# Define a testing slash command to make sure it works
@bot.tree.command(name="ask", description="Ask any question")
async def ask(interaction: discord.Interaction, question: str):
    response = f'You asked: "{question}". I don’t know how to answer yet!'
    await interaction.response.send_message(response)

# Sync command manually in case
@bot.command(name="sync")
async def sync(ctx: commands.Context):
    await bot.tree.sync()
    await ctx.send("slash commands synced")

# Run the bot
bot.run(TOKEN)
