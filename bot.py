import os
import time
import discord
from dotenv import load_dotenv
from google import genai  # Google's Gen AI SDK

# Load your secret keys from the .env file
load_dotenv()

# Initialize Discord Developer Intents and Client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Initialize the Gemini Client
# (It automatically grabs GEMINI_API_KEY from your .env file)
ai_client = genai.Client()

# Cooldown tracking memory
user_cooldowns = {}
COOLDOWN_SECONDS = 5.0

@client.event
async def on_ready():
    print(f"Successfully booted! We have logged in as {client.user}")

@client.event
async def on_message(message):
    # 1. Safety Check: Make sure the bot never talks to itself
    if message.author == client.user:
        return

    # 2. Convert text to lowercase for seamless case-insensitive matching
    text = message.content.lower()

    # -----------------------------------------------------------------
    # COMMAND 1: Case-Insensitive "Hi" with a 5-Second Cooldown
    # -----------------------------------------------------------------
    if text.startswith('hi'):
        user_id = message.author.id
        current_time = time.time()

        # Check if the user is spamming
        if user_id in user_cooldowns:
            time_passed = current_time - user_cooldowns[user_id]
            if time_passed < COOLDOWN_SECONDS:
                time_left = round(COOLDOWN_SECONDS - time_passed, 1)
                await message.channel.send(f"Whoa there, <@{user_id}>! Please wait {time_left} more seconds.")
                return  # Stop execution here

        # Pass check: update memory and reply
        user_cooldowns[user_id] = current_time
        await message.channel.send('Hello!')
        return

    # -----------------------------------------------------------------
    # COMMAND 2: Gemini "!ask" with 2000-Character Auto-Chunking
    # -----------------------------------------------------------------
    if text.startswith('!ask '):
        # Extract the question by slicing off the "!ask " prefix
        user_question = message.content[5:]

        try:
            # We build a custom rulebook telling Gemini about your friends and their IDs
            reference_rules = (
                "You are a fun Discord bot. You have access to a special mapping of friends' names and their keywords.\n"
                "If the user's question mentions any of these keywords, you MUST include their exact Discord ping tag "
                "character-for-character in your response so they get tagged:\n"
                "- Name: Cooper, Keywords 'peace', 'fat', or 'shannon' -> Ping <@576517577527001150>\n"
                "- Name: Soren, Keywords 'men', 'loli', or 'abused' -> Ping <@527278447894986753>\n"
                "- Name: Omar, Keywords 'shower', 'willpower', or 'prime' -> Ping <@608428956625928198>\n"
                "- Name: Arman, Keywords 'creative', 'crashout', 'feisty', 'cute', or 'devil' -> Ping <@719977618207801414>\n"
                "- Name: Shouvik, Keywords 'jail', 'fence', or 'weed' -> Ping <@501927322396655661>\n\n"
                "Keep your answers creative, direct, and under 3 sentences."
            )

            # Send the prompt to Gemini with our custom rules loaded in
            response = ai_client.models.generate_content(
                model='gemini-3.5-flash',
                contents=user_question,
                config={
                    'max_output_tokens': 1000,  
                    'system_instruction': reference_rules  # Gemini now reads the rules before responding!
                }
            )
            
            bot_reply = response.text
            
            # If the response fits in one Discord message, send it normally
            if len(bot_reply) <= 2000:
                await message.channel.send(bot_reply)
            else:
                for i in range(0, len(bot_reply), 2000):
                    await message.channel.send(bot_reply[i:i+2000])
            
        except Exception as e:
            print(f"Error encountered: {e}")
            await message.channel.send("Sorry, my brain hit a snag trying to process that response!")
            return

    # -----------------------------------------------------------------
    # COMMAND 3: VV References
    # -----------------------------------------------------------------
    # Splitting turns sentences into lists of words for structural processing
    words = text.split()

    VV_references = {
        "<@576517577527001150>": ["peace", "fat", "shannon"],
        "<@527278447894986753>": ["men", "loli", "abused"],
        "<@608428956625928198>": ["shower", "willpower", "prime"],
        "<@719977618207801414>": ["creative", "crashout", "feisty", "cute", "devil"],
        "<@501927322396655661>": ["jail", "fence", "weed"]
    }

    pings_to_send = set()

    for word in words:
        for friend_name, keywords in VV_references.items():
            if word in keywords:
                pings_to_send.add(friend_name)

    for friend_ping in pings_to_send:
        await message.channel.send(f"{friend_ping} reference!")          

# Launch the bot
client.run(os.getenv('DISCORD_TOKEN'))