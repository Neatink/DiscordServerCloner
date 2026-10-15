from dotenv import load_dotenv
from pathlib import Path
import discord
import base64
import json
import os

load_dotenv()
client = discord.Client()

JSON_ENCODING = "utf-8"
JSON_FILE_NAME = "channels.json"

@client.event
async def on_ready():
    while True:
        guild_action = input("Import/Export/List(i - import;e - export; l - list of guilds): ").lower()
        if guild_action == 'e':
            guild_name = input("Enter guild name to parse: ").lower()
            await export_guild(await get_guild(guild_name))
        elif guild_action == 'i':
            guild_import_create = input("Create new guild to import(y/n): ")
            if guild_import_create == 'y':
                await create_guild()
                #import
            elif guild_import_create == 'n':
                await get_guild(input("Enter guild name: "))
                #import
            else:
                print("What? Enter y or n; y - create new guild to import, n - export to exist guild")
        elif guild_action == 'l':
            for guild in client.guilds:
                print(f"{guild.name}(id:{guild.id})")
        else:
            print("What? Enter i or e; i - import guild, e - export guild")

async def get_guild(guild_name):
    for guild in client.guilds:
        if guild.name.lower() == guild_name:
            return guild
    print("This guild was not found! Maybe try again?")
    return None

async def create_guild():
    while True:
        guild_name = input("Enter guild name: ")
        guild_icon = input("Enter absolute path to icon image only PNG/JPG!(if exist): ").strip()
        guild_code = input("Enter guild template code(if exist): ").strip()
        args = {"name": guild_name}
        
        if guild_icon:
            guild_icon = Path(guild_icon)
            if guild_icon.is_file():
                with open(guild_icon, "rb") as image:
                    args["icon"] = image.read()
            else:
                print("Invalid icon image path! Maybe try again?")
                continue
                
        if guild_code:args["code"] = guild_code
        try:
            guild = await client.create_guild(**args)
            print(f"Successfully created guild '{guild_name}'!")
            return guild
        except discord.errors.NotFound as err:
            if err.code == 10057:
                print("Invalid template code! Maybe try again?")
        except discord.errors.HTTPException as err:
            if err.code == 50035:
                print("Guild name must be between 2 and 100 characters long! Maybe try again?")
        except TypeError:
            print("Invalid icon image path! Maybe try again?")
        
async def export_guild(guild):
    if not guild:return
    category_id = 0
    categories = []
    channels = []
    
    for channel in guild.channels:
        if isinstance(channel, discord.CategoryChannel):
            categories.append({"id": category_id, "name": channel.name})
            category_id += 1
        if not isinstance(channel, discord.CategoryChannel):
            temp_category_id = None
            for category_dict in categories:
                if channel.category and category_dict["name"] == channel.category.name:
                    temp_category_id = category_dict["id"]
                    
            if isinstance(channel, discord.TextChannel):
                channels.append({"name": channel.name, "category_id": temp_category_id, "position": channel.position, "topic": channel.topic,
                                 "nsfw": channel.nsfw, "slowmode_delay": channel.slowmode_delay, "default_auto_archive_duration": channel.default_auto_archive_duration,
                                 "news": channel.is_news()})
            elif isinstance(channel, discord.VoiceChannel):
                channels.append({"name": channel.name, "category_id": temp_category_id, "position": channel.position, "bitrate": channel.bitrate,
                                 "nsfw": channel.nsfw, "slowmode_delay": channel.slowmode_delay, "user_limit": channel.user_limit,
                                 "video_quality": channel.video_quality_mode, "rtc_region": channel.rtc_region}) #rtc_region if None = Auto-Select
            elif isinstance(channel, discord.ForumChannel):
                tags = []
                for tag in channel.available_tags:
                    tags.append({"name": tag.name, "emoji": str(tag.emoji) if tag.emoji else None, "moderated": tag.moderated,
                                 "url": tag.emoji.url if (tag.emoji and tag.emoji.is_custom_emoji()) else None})
                    
                channels.append({"name": channel.name, "category_id": temp_category_id, "position": channel.position, "topic": channel.topic,
                                 "nsfw": channel.nsfw, "slowmode_delay": channel.slowmode_delay, "default_auto_archive_duration": channel.default_auto_archive_duration,
                                 "default_reaction_emoji": channel.default_reaction_emoji.name if channel.default_reaction_emoji else None, "available_tags": tags,
                                 "require_tag": channel.flags.require_tag,"default_sort_order": channel.default_sort_order,
                                 "default_thread_slowmode_delay": channel.default_thread_slowmode_delay,"default_layout": channel.default_layout})
            elif isinstance(channel, discord.StageChannel):
                channels.append({"name": channel.name, "category_id": temp_category_id, "position": channel.position, "bitrate": channel.bitrate,
                                 "nsfw": channel.nsfw, "slowmode_delay": channel.slowmode_delay,"user_limit": channel.user_limit, "video_quality": channel.video_quality_mode})
    with open(JSON_FILE_NAME, 'w', encoding=JSON_ENCODING) as f:
        avatar = base64.b64encode(await guild.icon.read()).decode() if guild.icon else None
        json.dump({"avatar": avatar, "categories": categories, "channels": channels}, f, ensure_ascii=False, indent="\t")
    print("Successfully!")

client.run(os.getenv("DISCORD_TOKEN"))