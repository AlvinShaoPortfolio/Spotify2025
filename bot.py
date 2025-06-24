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
            name, album_cover = await app.get_album_cover_and_name()
            
            embed = discord.Embed(
                title = name,
                description = "react with any emote to claim!",
                color=discord.Color.green()
            )
            embed.set_image(url = album_cover)

            await message.channel.send(embed = embed)

intents = discord.Intents.default() #what the bot can interact with
intents.message_content = True

client = MyClient(intents = intents) #start the bot
client.run(DISCORD_TOKEN)