import os
import discord
import math
import psycopg2
from discord.ext import commands

# set global vars
bot_name = "rpg-bot#4333"
discord_token = os.environ["PY_VAR_RPGBOT_TOKEN"]
database_url = os.environ["DATABASE_URL"]
database_user = database_url.split(":")[1].replace("/", "")
database_password, database_host = database_url.split(":")[2].split("@")
database_name = database_url.split("/")[-1]
database_port = 5432

# set bot 
bot = commands.Bot(command_prefix="!")

# connect to discord
client = discord.Client()

# open sqlite database
con = psycopg2.connect(
    dbname=database_name, 
    user=database_user, 
    password=database_password, 
    host=database_host, 
    port=database_port)

cur = con.cursor()

def create_tables():

    # create experience table
    cur.execute('''CREATE TABLE if not exists experience
                (id serial primary key, 
                guild text, 
                discord_user text, 
                experience int, 
                level int,
                skill_points int not null)''')
    # create stats table
    cur.execute('''CREATE TABLE if not exists stats
                (id serial primary key,
                experience_id serial not null, 
                strength int not null,
                dexterity int not null,
                luck int not null,
                foreign key (experience_id) references experience (id))''')
    con.commit()


async def give_experience(guild, user, channel_id, amount=1):

    # format user/guild for query
    guild_formatted = guild.replace("'", "''").replace('"', '""')
    user_formatted = user.replace("'", "''").replace('"', '""')

    # get experience 
    cur.execute(f"select * from experience where discord_user = '{user_formatted}' and guild = '{guild_formatted}'")
    data = cur.fetchone() 

    # if no return values add in a row
    if data is None:
        experience_points = amount
        level = 0
        skill_points = 0
        cur.execute(f"insert into experience (guild, discord_user, experience, level, skill_points) values (%s, %s, %s, %s, %s)", (guild, user, experience_points, level, skill_points))
        con.commit()

    else:
        id, guild, user, experience, level, skill_points = data
        experience_points = experience + amount
        cur.execute(f"update experience set experience = {experience_points} where id = {id}")
        con.commit()

    print(f'{guild}: {user} is at {experience_points} experience')

    # check to see if they can level up
    await check_level(guild_formatted, user_formatted, experience_points, level, skill_points, channel_id)


async def check_level(guild, user, experience, level, skill_points, channel_id):

    # get the amount needed for the next level
    # if we have enough level up the user
    needed_exp = await get_exp_needed(level)
    # print(f"needed: {needed_exp}, has: {experience}")
    if experience >= needed_exp:
        level = level + 1
        skill_points = skill_points + 1
        experience = experience - needed_exp
        cur.execute(f"update experience set experience = {experience}, level = {level} , skill_points = {skill_points} where discord_user = '{user}' and guild = '{guild}'")
        con.commit()
        print(f"{guild}: {user} is now at level {level} with {experience} experience")
        user_formatted = "#".join(user.split("#")[:-1])
        ch = await bot.fetch_channel(int(channel_id))
        await ch.send(f"{user_formatted} is now at level {level}!\n\tSkill Points: {skill_points}")


async def get_exp_needed(level):

    exponent = 1.5
    base_xp = 5
    return math.floor(base_xp * (level ** exponent))


# ensure tables are created
create_tables()

@bot.event
async def on_ready():
    print("Connected to Discord!")


@bot.event
async def on_message(message):
#    if 'https://' in message.content:
#       await message.delete()
    if bot_name != str(message.author):
        guild_name = message.channel.guild.id
        user_name = message.author
        await give_experience(str(guild_name), str(user_name), message.channel.id, 1)
        await bot.process_commands(message)
        
        # print(message.author.mention)
        # print(dir(message))
        # print(dir(message.system_content))
        # print(message.author.name)
        # print(dir(message.channel.guild))
        # await message.channel.send(f"{message.author.mention} said {message.content}")

@bot.event
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

@bot.command()
async def spend_skill_point(ctx, stat):

    # set allowed values
    allowed_stats = [
        "strength",
        "dexterity",
        "luck"
    ]

    # check if any skill points are available
    user = ctx.author.name
    guild = ctx.guild.id
    cur.execute(f"select skill_points from experience where discord_user = '{user}' and guild = '{guild}'")
    data = cur.fetchone()
    if data is not None:
        skill_points = data[0]
        if skill_points > 0:
            if stat in allowed_stats:
                print("ALLOWED")
            else:
                print(stat)
        else:
            print(dir(ctx))
            ctx.send(f"{stat} is not an allowed stat. Try strength, dexterity, or luck.")



bot.run(discord_token)
#client.run(discord_token)