from dotenv import load_dotenv
import discord
import json
import os

load_dotenv()
client = discord.Client()

JSON_ENCODING = "utf-8"
JSON_FILE_NAME = "channels.json"

@client.event
async def on_ready():
    guild_name = input("Enter guild name to parse: ").lower()
    for guild in client.guilds:
        if guild.name.lower() == guild_name:
            await create_categories(guild)

async def create_categories(guild):
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
        json.dump({"categories": categories, "channels": channels}, f, ensure_ascii=False, indent="\t")
    print("Successfully!")

client.run(os.getenv("DISCORD_TOKEN"))