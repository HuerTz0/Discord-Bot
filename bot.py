# bot.py
import os
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
#Test Code
@client.event
async def on_message(message):
  if message.author == client.user:
    return
  if message.content.startswith('Hi'):
    await message.channel.send('Hello')


# start the bot


client.run(TOKEN)