import os
import discord

bot_name = "rpg-bot#4333"
discord_token = os.environ["PY_VAR_RPGBOT_TOKEN"]

# connect to discord
client = discord.Client()

@client.event
async def on_ready():
    print("Connected to Discord!")

@client.event
async def on_message(message):
#    if 'https://' in message.content:
#       await message.delete()
    if bot_name != str(message.author):
        # print(message.author.mention)
        # print(dir(message.author))
        # print(message.author.name)
        await message.channel.send(f"{message.author.mention} said {message.content}")

client.run(discord_token)