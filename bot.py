# bot.py
import os
import time
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
user_cooldowns = {}
COOLDOWN_SECONDS = 5.0

@client.event
async def on_message(message):
    # Ignore the bot's own messages
    if message.author == client.user:
        return

    text = message.content.lower()

    if text.startswith('hi'):
        user_id = message.author.id
        current_time = time.time()

        # Check if the user is in our memory AND if 5 seconds haven't passed yet
        if user_id in user_cooldowns:
            time_passed = current_time - user_cooldowns[user_id]
            if time_passed < COOLDOWN_SECONDS:
                # Math to figure out exactly how long they have left
                time_left = round(COOLDOWN_SECONDS - time_passed, 1)
                await message.channel.send(f"Whoa there, <@{user_id}>! Please wait {time_left} more seconds.")
                return # Stop the code here so they don't get a 'Hello'

        # If they aren't on cooldown, update their timestamp in the memory
        user_cooldowns[user_id] = current_time

        # Finally, send the actual response!
        await message.channel.send('Hello')

client.run(TOKEN)