import discord
import os
import app
from dotenv import load_dotenv #lets me load the env file
from firebase_handler import store_claimed_song
from firebase_handler import check_song_in_server
from firebase_handler import store_in_server

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
            song_id, song_name, album_cover, album_name, song_points, chosen_artist_name = await app.get_song_info()

            server_id = message.guild.id
            is_song_in_server = check_song_in_server(server_id, song_id)

            if is_song_in_server:
                embed = discord.Embed(
                    title = f"{song_name} - by {chosen_artist_name}",
                    description = (
                            f"{album_name}\n" 
                            f"**{song_points}** 🎵\n"
                            ),
                    color=discord.Color(0xFF0000)
                )
            else:
                embed = discord.Embed(
                    title = f"{song_name} - by {chosen_artist_name}",
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
                "id": song_id,
                "name": song_name,
                "album": album_name,
                "points": song_points,
                "artist": chosen_artist_name,
                "claimed": False
            }

            if(not is_song_in_server):
                await embed_message.add_reaction("🎵")
    
    async def on_reaction_add(self, reaction, user):
        if user == client.user: #prevents it from detecting itself
            return
        
        if reaction.emoji == "🎵":

            message_id = reaction.message.id
            server_id = reaction.message.guild.id
            claimed_song = song_claim_map.get(message_id)
                
            if claimed_song and claimed_song.get("claimed"): 
                await reaction.message.channel.send(f"🎶 **name** already claimed this song **{claimed_song['name']}** 🎶")
            else:
                print(claimed_song)

                store_in_server(server_id, claimed_song["id"], user.id, claimed_song["name"]) #store in server to check for dupes later
                store_claimed_song(user.id, user.name, claimed_song) #store within the user inventory

                song_claim_map[message_id]["claimed"] = True

                await reaction.message.channel.send(f"🎶 **{user.display_name}** is jamming out to **{claimed_song['name']}** 🎶")


intents = discord.Intents.default() #what the bot can interact with
intents.message_content = True
intents.reactions = True

client = MyClient(intents = intents) #start the bot
client.run(DISCORD_TOKEN)