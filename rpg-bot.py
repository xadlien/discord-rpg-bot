import os
import discord
import math
import sqlite3

# set global vars
bot_name = "rpg-bot#4333"
discord_token = os.environ["PY_VAR_RPGBOT_TOKEN"]
message_file = "./message_history"
message_delimiter = "||//??"

# open message history file to save for AI
outfile = open(message_file, "a")

# connect to discord
client = discord.Client()

# open sqlite database
con = sqlite3.connect('rpg-bot.db')
cur = con.cursor()

def create_tables():

    # Create table
    cur.execute('''CREATE TABLE if not exists experience
                (guild text, user text, experience integer, level integer)''')
    con.commit()


async def give_experience(guild, user, channel_id, amount=1):

    # format user/guild for query
    guild_formatted = guild.replace("'", "''").replace('"', '""')
    user_formatted = user.replace("'", "''").replace('"', '""')

    # get experience 
    cur.execute(f"select * from experience where user = '{user_formatted}' and guild = '{guild_formatted}'")
    data = cur.fetchone() 

    # if no return values add in a row
    if data is None:
        experience_points = amount
        level = 0
        cur.execute(f"insert into experience values (?, ?, ?, ?)", (guild, user, experience_points, level))
        con.commit()

    else:
        guild, user, experience, level = data
        experience_points = experience + amount
        cur.execute(f"update experience set experience = {experience_points} where user = '{user_formatted}' and guild = '{guild_formatted}'")
        con.commit()

    print(f'{guild}: {user} is at {experience_points} experience')

    # check to see if they can level up
    await check_level(guild_formatted, user_formatted, experience_points, level, channel_id)


async def check_level(guild, user, experience, level, channel_id):

    # get the amount needed for the next level
    # if we have enough level up the user
    needed_exp = await get_exp_needed(level)
    # print(f"needed: {needed_exp}, has: {experience}")
    if experience >= needed_exp:
        level = level + 1
        experience = experience - needed_exp
        cur.execute(f"update experience set experience = {experience}, level = {level} where user = '{user}' and guild = '{guild}'")
        con.commit()
        print(f"{guild}: {user} is now at level {level} with {experience} experience")
        user_formatted = "#".join(user.split("#")[:-1])
        ch = await client.fetch_channel(int(channel_id))
        await ch.send(f"{user_formatted} is now at level {level}!")


async def get_exp_needed(level):

    exponent = 1.5
    base_xp = 5
    return math.floor(base_xp * (level ** exponent))


# ensure tables are created
create_tables()

@client.event
async def on_ready():
    print("Connected to Discord!")


@client.event
async def on_message(message):
#    if 'https://' in message.content:
#       await message.delete()
    if bot_name != str(message.author):
        outfile.write(message.content + "\n")
        outfile.write(message_delimiter + "\n")
        guild_name = message.channel.guild.id
        user_name = message.author
        await give_experience(str(guild_name), str(user_name), message.channel.id, 1)
        
        # print(message.author.mention)
        # print(dir(message))
        # print(dir(message.system_content))
        # print(message.author.name)
        # print(dir(message.channel.guild))
        # await message.channel.send(f"{message.author.mention} said {message.content}")

@client.event
async def on_raw_reaction_add(payload):
    # print(dir(payload))
    # print(payload.member)
    # print(payload.user_id)
    # print(payload.guild_id)
    # print(payload.channel_id)
    if bot_name != str(payload.member):
        guild_name = str(payload.guild_id)
        user_name = str(payload.member)
        await give_experience(guild_name, user_name, payload.channel_id, 1)

client.run(discord_token)