import discord
import os
import app

from dotenv import load_dotenv #lets me load the env file
from firebase_handler import store_claimed_song

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

song_claim_map = {} #temp store song when they emote

class MyClient(discord.Client):
    async def on_ready(self): #starts the bot
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message): #waits for a message and sends a response
        if message.author == self.user:
            return
        
        if message.content.startswith('$music'):
            name, album_cover, album_name, song_points, chosen_artist_name = await app.get_song_info()
            
            embed = discord.Embed(
                title = f"{name} - by {chosen_artist_name}",
                description = (
                            f"{album_name}\n" 
                            f"**{song_points}** 🎵\n"
                            "Click the music emoji to claim!" 
                            ),
                color=discord.Color(0x1DB954)
            )
            embed.set_image(url = album_cover)

            embed_message = await message.channel.send(embed = embed)

            song_claim_map[embed_message.id] = {
                "name": name,
                "album": album_name,
                "points": song_points,
                "artist": chosen_artist_name,
                "claimed": False
            }

            await embed_message.add_reaction("🎵")
    
    async def on_reaction_add(self, reaction, user):
        if user == client.user: #prevents it from detecting itself
            return
        
        if reaction.emoji == "🎵":
            message_id = reaction.message.id

            claimed_song = song_claim_map.get(message_id)

            if claimed_song:
                print(claimed_song)
                claimed_song["claimed"] = True
                
                store_claimed_song(user.name, claimed_song)

                await reaction.message.channel.send(f"🎶 **{user.name}** is jamming out to **{claimed_song['name']}** 🎶")


intents = discord.Intents.default() #what the bot can interact with
intents.message_content = True
intents.reactions = True

client = MyClient(intents = intents) #start the bot
client.run(DISCORD_TOKEN)