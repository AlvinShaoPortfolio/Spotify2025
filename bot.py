import discord
import os
import app

from dotenv import load_dotenv #lets me load the env file

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

class MyClient(discord.Client):
    async def on_ready(self): #starts the bot
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message): #waits for a message and sends a response
        if message.author == self.user:
            return
        
        if message.content.startswith('$music'):
            name, album_cover, album_name, song_points = await app.get_album_cover_and_name()
            
            embed = discord.Embed(
                title = name,
                description = (
                            f"{album_name}\n" 
                            f"**{song_points}** 🎵\n"
                            "React with any emote to claim!" 
                            ),
                color=discord.Color(0x1DB954)
            )
            embed.set_image(url = album_cover)

            await message.channel.send(embed = embed)

intents = discord.Intents.default() #what the bot can interact with
intents.message_content = True

client = MyClient(intents = intents) #start the bot
client.run(DISCORD_TOKEN)