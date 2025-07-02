import discord
import os
import app

from math import ceil
from discord.ui import View, Button #interactive buttons for $collection
from dotenv import load_dotenv #lets me load the env file
from firebase_handler import store_claimed_song
from firebase_handler import check_song_in_server
from firebase_handler import store_in_server
from firebase_handler import retrieve_song_holder
from firebase_handler import user_already_claimed_song
from firebase_handler import return_all_songs
from firebase_handler import return_total_popularity

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

song_claim_map = {}#temp store song when they emote

class MyClient(discord.Client):
    async def on_ready(self): #starts the bot
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message): #waits for a message and sends a response
        if message.author == self.user:
            return
        
        if message.content.lower().startswith('$pop'):
            server_id = str(message.guild.id)
            user_id = str(message.author.id)
            total_popularity = return_total_popularity(server_id, user_id)

            embed = discord.Embed(
                title="🌟 Total Popularity Score 🌟",
                description=(
                    f"**{message.author.display_name}**, your claimed songs have a combined popularity value of:\n\n"
                    f"🎵 **{total_popularity:,} points!**"
                ),
                color=discord.Color.pink()
            )

            embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else discord.Embed.Empty)
            embed.set_footer(text="Keep claiming songs to grow your collection!")

            await message.channel.send(embed=embed)
            
        #---------------------------------------------------------------------------------------------------------------------------

        if message.content.lower().startswith('$collection'):
            server_id = message.guild.id
            user_id = str(message.author.id)
            claimed_songs = return_all_songs(server_id, user_id)

            if not claimed_songs:
                await message.channel.send("You haven't claimed any songs yet.")
                return

            view = CollectionView(message.author, claimed_songs)
            embed = view.build_embed()
            await message.channel.send(embed=embed, view=view)

        #--------------------------------------------------------------------------------------------------------------------------------------    
        
        if message.content.lower().startswith('$music'):
            song_id, song_name, album_cover, album_name, song_points, chosen_artist_name = await app.get_song_info()

            server_id = message.guild.id
            is_song_in_server = check_song_in_server(server_id, song_id)

            if is_song_in_server:
                embed = discord.Embed(
                    title = f"{song_name} - by {chosen_artist_name}",
                    description = (
                            f"{album_name}\n" 
                            f"**{song_points}** 🎵\n"
                            f"Owned by **{retrieve_song_holder(server_id, song_id)}**"
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
        if user == self.user: #prevents it from detecting itself
            return

        message_id = reaction.message.id
        server_id = reaction.message.guild.id
        claimed_song = song_claim_map.get(message_id)
        
        if reaction.emoji == "🎵":
            if claimed_song and not claimed_song.get("claimed") and not check_song_in_server(server_id, claimed_song.get("id")): #checking the session because firebase isnt fast enough if you directly claim after someone else claims
                if user_already_claimed_song(server_id, user.id, claimed_song["id"]): #checking firebase for the songs that were claimed outside the session ------------------------------------------------------------ other people can claim react to your claimed songs because im not checking serverside
                    return
                store_in_server(server_id, claimed_song["id"], user.id, claimed_song["name"]) #store in server to check for dupes later
                store_claimed_song(server_id, user.id, user.name, claimed_song) #store within the user inventory

                song_claim_map[message_id]["claimed"] = True
                print(claimed_song)

                await reaction.message.channel.send(f"🎶 **{user.display_name}** is jamming out to **{claimed_song['name']}** 🎶")
        

class CollectionView(View): #the interactive button for $colleciton
    def __init__(self, user, claimed_songs, *, timeout=60):
        super().__init__(timeout=timeout)
        self.user = user
        self.claimed_songs = claimed_songs
        self.page = 0

    def build_embed(self):
        total_pages = ceil(len(self.claimed_songs) / 10)
        start = self.page * 10
        end = start + 10

        embed = discord.Embed(
            title=f"🏆 {self.user.display_name}'s Top Songs",
            description="These are your top songs by popularity value!",
            color=discord.Color.gold()
        )

        for i, song in enumerate(self.claimed_songs[start:end], start=start + 1):
            embed.add_field(
                name=f"#{i} - {song.get('song_name', 'Unknown Song')} 🎶 - by {song.get('artist_name', 'Unknown Artist')}",
                value=f"{song.get('album_name', 'Unknown Album')}\nPopularity Value: {song.get('points', 0)}",
                inline=False
            )

        embed.set_footer(text=f"Page {self.page + 1} / {total_pages}")
        return embed

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.user:
            await interaction.response.send_message("This isn't your collection.", ephemeral=True)
            return

        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.user:
            await interaction.response.send_message("This isn't your collection.", ephemeral=True)
            return

        max_page = ceil(len(self.claimed_songs) / 10) - 1
        if self.page < max_page:
            self.page += 1
            await interaction.response.edit_message(embed=self.build_embed(), view=self)

intents = discord.Intents.default() #what the bot can interact with
intents.message_content = True
intents.reactions = True

client = MyClient(intents = intents) #start the bot
client.run(DISCORD_TOKEN)