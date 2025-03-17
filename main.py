import asyncio
import io 
import os
import random
import sqlite3
from datetime import datetime, timedelta
from typing import Union
import ffmpeg
from googleapiclient.discovery import build
import discord
import requests
import re
import yt_dlp as youtube_dl
from discord.ext import commands
from discord.ext.commands import BucketType, cooldown
from PIL import Image, ImageDraw, ImageFont, ImageOps
import platform
import psutil
import keep_alive
from character import character_images
from op_characters import character_images_op
import opuslib


KEY = os.environ['TOKEN']
API_KEY = 'AIzaSyCyo93BP9QL4qlQzgwepf9yFkBeJD3iawk'
intents = discord.Intents.all()


bot = commands.Bot(command_prefix='$',intents=intents)


bot.remove_command('help')

k_id = 797057126707101716

# Database setup
connection = sqlite3.connect('xp_data.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS xp_data (
                    user_id INTEGER PRIMARY KEY,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    user_game_count INTEGER DEFAULT 0,
                    last_played TEXT DEFAULT NULL
                )''')

connection.commit()




#games battle setup 
target_channel_id = 1166317975557644318
message_threshold = 10
message_counter = 0
is_game_active = False

#bot on ready startup
@bot.event
async def on_ready():
    
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Messages"))
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.channel.id == target_channel_id:
        global message_counter
        message_counter += 1

        if message_counter >= message_threshold and not is_game_active:
            await spawn_game(message.channel)
            message_counter = 0 

    await bot.process_commands(message)




 #------------------------------------------------------------------------------------
#help
@bot.command()
async def help(ctx,which=None):
  if(which== "oreo"): #oreos
   embed = discord.Embed(title='Heres commands for oreos',
                         description="",
                         color= 0x4d94ff )

   embed.add_field(name="`$bal`",value='Shows how much oreos you have')
   embed.add_field(name="`$wd`",value='Withdraws oreos from bank to wallet')
   embed.add_field(name="`$dep`",value='Deposits oreos from wallet to bank')
   embed.add_field(name="`$shop`",value='Shows purchasable roles and items')
   embed.add_field(name="`$lb`",value='Displays the leadboard of oreos')

   await ctx.send(embed=embed)

  elif(which=="eco"):
    embed = discord.Embed(title='Heres commands for oreos',
     description="",
     color= 0x4d94ff )
    embed.add_field(name="`$daily`",value='Earn 250-250 oreos,cooldown 24h ')
    embed.add_field(name="`$make`",value='Earn 100-200 oreos,cooldown 6h ')

    await ctx.send(embed=embed)

  elif(which=="commands"):  # COMMANDS


    embed = discord.Embed(title='Heres some basic commands',
                          description="\n",
                          color= 0x4d94ff )
    embed.add_field(name="`$ping`",value='Checks the bots response time and latency. ')
    embed.add_field(name="`$rate`",value='Rates the mentioned user ou of 10. ')
    embed.add_field(name="`$snipe`",value='Shows the recently deleted message in that channel')
    embed.add_field(name="`$hug`",value='Sends a hug gif for the mentioned user')


    await ctx.send(embed=embed)
  else :
    icon_url = 'https://images-ext-2.discordapp.net/external/7YyT6QYqe05EwGhEX5mR6Gn86F9NpnjOZ6DfkZjpvdA/%3Fsize%3D4096/https/cdn.discordapp.com/avatars/1147534992910585916/d3b90d801eab42da264223daea0c43ee.png'
    user = ctx.message.author
    embed = discord.Embed(title=f'{user.mention}',description="\n",color=0x4d94ff )
    embed.set_author(name='Oreo tree Bot | Help')
    embed.add_field(name='oreo',value="`$help oreo` ")

    embed.add_field(name="eco",value="`$help eco` ")

    embed.add_field(name=" Basic Commands",value="`$help commands` ")
    embed.set_thumbnail(url=icon_url)
    await ctx.send(embed=embed) 

#-------------------------------------------------------------------------------------


daily_cooldowns = {}
@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user)  
async def daily(ctx):
    user_id = str(ctx.author.id)

    if user_id in daily_cooldowns:
        last_claimed = daily_cooldowns[user_id]
        time_difference = datetime.now() - last_claimed

        remaining_time = timedelta(seconds=86400) - time_difference
        remaining_hours, remainder = divmod(remaining_time.seconds, 3600)
        remaining_minutes, _ = divmod(remainder, 60)

        await ctx.send(f"Cooldown for your next daily: {remaining_hours} hours and {remaining_minutes} minutes.")
    else:
        reward = random.randint(250, 350)
        cursor.execute('INSERT OR IGNORE INTO xp_data (user_id) VALUES (?)', (user_id,))
        cursor.execute('UPDATE xp_data SET xp = xp + ? WHERE user_id = ?', (reward, user_id))
        connection.commit()
        daily_cooldowns[user_id] = datetime.now()
        await ctx.send(f"Congratulations! You earned {reward} Oreos.")

@daily.error
async def daily_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        remaining_time = error.retry_after
        remaining_hours, remainder = divmod(remaining_time, 3600)
        remaining_minutes, _ = divmod(remainder, 60)

        await ctx.send(f"You are currently on cooldown, try again in `{int(remaining_hours)}` hours  `{int(remaining_minutes)}` minutes.")


#------------------------------------------------------------------------------------

#make
manufactuer_cooldowns = {}

@bot.command()
@commands.has_any_role('manufacturer')
@commands.cooldown(1, 21600, commands.BucketType.user)  
async def make(ctx):
    user_id = str(ctx.author.id)

    if user_id in daily_cooldowns:
        last_claimed = manufactuer_cooldowns[user_id]
        time_difference = datetime.now() - last_claimed

        remaining_time = 86400 - time_difference.total_seconds()
        remaining_time = str(timedelta(seconds=int(remaining_time)))

        await ctx.send(f"Cooldown for your next manufactuer{remaining_time}.")
    else:

        reward = random.randint(100, 200)  
        cursor.execute('UPDATE xp_data SET xp = xp + ? WHERE user_id = ?', (reward, user_id))

        connection.commit()
        daily_cooldowns[user_id] = datetime.now()

        await ctx.send(f"`You Made {reward} Oreos.`")

@make.error
async def make_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
      remaining_time = error.retry_after
      hours, remainder = divmod(remaining_time, 3600)
      minutes, seconds = divmod(remainder, 60)

      message = (
          f"Sorry, you can make Oreos again in **{int(hours)} hours, "
          f"**{int(minutes)} minutes, and **{int(seconds)} seconds**."
      )
      await ctx.send(message)


#-------------------------------------------------------------------------------------

# Ping command
@bot.command(help='Use $ping to see bot response time')
async def ping(ctx):
    latency = round(bot.latency * 1000)  
    embed = discord.Embed(title=f'Pong! Response time: {latency} ms')
    await ctx.send(embed=embed)
#------------------------------------------------------------------------------------
#message delete command
@bot.command(help='Use $msgdel to delete messages \\(Only can be used by Mods) ')
@commands.has_any_role('_______FOUNDER_______', 'Mod')
async def msgdel(ctx, amount: int):
  if amount == 0:
    await ctx.send('Invalid amount!')
    return 

  await ctx.channel.purge(limit=amount + 1)

@msgdel.error
async def msgdel(ctx, error):
  if isinstance(error, commands.MissingRole):
    await ctx.send('You do not have permission to use that command!')

#------------------------------------------------------------------------------------

# Game command
@bot.command()
async def game(ctx, option=None):
  daily_game_limit = 30
  user_id = ctx.author.id
  current_time = datetime.now()
  cursor.execute('SELECT user_game_count FROM xp_data WHERE user_id = ?', (user_id,))
  user_game_count_result = cursor.fetchone()
  user_game_count = user_game_count_result[0] if user_game_count_result else 0


  cursor.execute('INSERT OR IGNORE INTO xp_data (user_id) VALUES (?)', (user_id,))
  connection.commit()

  cursor.execute("SELECT last_played, user_game_count FROM xp_data WHERE user_id = ?", (user_id,))
  user_data = cursor.fetchone()

  if user_data:
      last_played, user_game_count = user_data

      if last_played:
          # Calculate the time difference
          time_difference = current_time - datetime.fromisoformat(last_played)

          # If more than 24 hours have passed, reset the game count
          if time_difference.days >= 1:
              user_game_count = 0

      user_game_count += 1
      cursor.execute('UPDATE xp_data SET user_game_count = ?, last_played = ? WHERE user_id = ?',
                     (user_game_count, current_time.isoformat(), user_id))
  else:
      # If user is new, initialize the data
      user_game_count = 1
      cursor.execute('INSERT INTO xp_data (user_id, user_game_count, last_played) VALUES (?, ?, ?)',
                     (user_id, user_game_count, current_time.isoformat()))

  connection.commit()

  if user_game_count > daily_game_limit:
      await ctx.send("You've reached the daily game limit. Try again tomorrow!")
      return

  correct_reward = random.randint(19, 32)
  allowed_channel_id = [1166294561300168735, 1166473829195984977, 1166473801056387163]
  if ctx.channel.id not in allowed_channel_id:
      await ctx.send("This command can only be used in oreo chats")
      return

  character_data = character_images_op if option == 'op' else character_images 

  character_entry = random.choice(list(character_data.items()))
  character_name = character_entry[0]
  alternative_names = character_entry[1]['names']
  image_url = character_entry[1]['image'] 

  cursor.execute('SELECT user_game_count FROM xp_data WHERE user_id = ?', (user_id,))
  user_game_count = cursor.fetchone()

  embed = discord.Embed(title='Character Guessing Game')
  embed.set_image(url=image_url)
  embed.set_footer(text='Type the character name to guess.')

  await ctx.send(embed=embed)

  def check(message):
      return message.author == ctx.author

  try:
      user_guess = await bot.wait_for('message', timeout=15, check=check)
      guess = user_guess.content.capitalize()   

      if guess.lower() in [name.lower() for name in alternative_names]:
          # Correct guess
          user_id = ctx.author.id
          cursor.execute('SELECT user_game_count FROM xp_data WHERE user_id = ?', (user_id,))
          user_game_count_result = cursor.fetchone()
          user_game_count = user_game_count_result[0] if user_game_count_result else 0
          cursor.execute('INSERT OR IGNORE INTO xp_data (user_id) VALUES (?)', (user_id,))
          cursor.execute('UPDATE xp_data SET xp = xp + ? WHERE user_id = ?', (correct_reward, user_id))
          connection.commit()

          games_left = max(0, daily_game_limit - user_game_count)

          embed = discord.Embed(title='Correct!', description=f'💰 You won **{correct_reward}** oreos')
          embed.add_field(name='Possible Answers', value=f'{character_name}', inline=False)
          embed.add_field(name='',value=f'You have {games_left} games remaining!')
          await ctx.send(embed=embed)

      else: 
          cursor.execute('SELECT user_game_count FROM xp_data WHERE user_id = ?', (user_id,))
          user_game_count_result = cursor.fetchone()
          user_game_count = user_game_count_result[0] if user_game_count_result else 0
          games_left = max(0, daily_game_limit - user_game_count)
          # Incorrect guess
          embed = discord.Embed(title='Incorrect', description='❌ You did not answer correctly.')
          embed.add_field(name='Possible Answers', value=f'{character_name}', inline=False)
          embed.add_field(name='',value=f'You have {games_left} games remaining!')
          await ctx.send(embed=embed)

  except asyncio.TimeoutError:
      cursor.execute('SELECT user_game_count FROM xp_data WHERE user_id = ?', (user_id,))
      user_game_count_result = cursor.fetchone()
      user_game_count = user_game_count_result[0] if user_game_count_result else 0
      games_left = max(0, daily_game_limit - user_game_count)
      embed = discord.Embed(title='Incorrect', description='❌ You did not answer correctly.')
      embed.add_field(name='Possible Answers', value=f'{character_name}', inline=False)
      embed.add_field(name='',value=f'You have {games_left} games remaining!')
      await ctx.send(embed=embed)


async def spawn_game(channel):
  global is_game_active 
  is_game_active = True

  character_entry = random.choice(list(character_images.items()))
  character_entry[0]
  character_name = character_entry[0]
  alternative_names = character_entry[1]['names']
  image_url = character_entry[1]['image']

  embed = discord.Embed(title='Character Guessing Game')
  embed.set_image(url=image_url)
  embed.set_footer(text='Type the character name to guess.')

  await channel.send(embed=embed)

  def check(message):
      return message.author == message.author and message.channel == channel

  correct_guess = False

  try:
      while True:
          user_guess = await bot.wait_for('message', timeout=15, check=check)
          guess = user_guess.content.capitalize()

          if guess.lower() in [name.lower() for name in alternative_names]:
              # Correct guess
              user_id = user_guess.author.id

              correct_reward = random.randint(15, 30)

              cursor.execute('INSERT OR IGNORE INTO xp_data (user_id) VALUES (?)', (user_id,))
              cursor.execute('UPDATE xp_data SET xp = xp + ? WHERE user_id = ?', (correct_reward, user_id))

              connection.commit()

              embed = discord.Embed(title=f'Correct! You gain {correct_reward} Oreos!')
              await channel.send(embed=embed)

              correct_guess = True
              break
          else:
              # Incorrect guess, delete the user's message
              await user_guess.delete()
  except asyncio.TimeoutError:
      if not correct_guess:
          embed = discord.Embed(title=f"Time's up! It was {character_name}.")
          await channel.send(embed=embed)

  is_game_active = False
  # Do not delete the game message here, only incorrect user guesses
#------------------------------------------------------------------------------------

# Leaderbord command
@bot.command()
async def lb(ctx):
    cursor.execute('SELECT user_id, xp FROM xp_data ORDER BY xp DESC LIMIT 10')
    leaderboard_data = cursor.fetchall()

    guild = bot.get_guild(1166279947078336542)  

    embed = discord.Embed(title='Oreo Leaderboard', color=discord.Color.blue())
    for index, (user_id, xp) in enumerate(leaderboard_data, start=1):
        member = guild.get_member(user_id)
        if member:
            embed.add_field(name=f'{index}. {member.name}', value=f'XP: {xp}', inline=False)
        else:
            embed.add_field(name=f'{index}. Unknown User', value=f'XP: {xp}', inline=False)

    await ctx.send(embed=embed)


  #-----------------------------------------------------------------------------------



#bal
@bot.command()
async def bal(ctx, user: discord.User = None):
    background_url = 'https://cdn.discordapp.com/attachments/1166294561300168735/1167720973034852402/20231028_123557.jpg?ex=654f27e7&is=653cb2e7&hm2bccee8bc478653c7cbd09c9656fb875797720f36f30b85204b80c84d01244a9&'
    background_response = requests.get(background_url)
    background_image = Image.open(io.BytesIO(background_response.content))

    user_id = ctx.author.id if user is None else user.id

    cursor.execute('SELECT xp, level FROM xp_data WHERE user_id = ?', (user_id,))
    data = cursor.fetchone()

    if data is None:
        await ctx.send("User data not found.")
    else:
        xp, level = data  # that scared me fr , i was at down all turned orange 
    cursor.execute('SELECT bank FROM xp_data WHERE user_id = ?', (user_id,))
    bank = cursor.fetchone()

    if data is None:
      await ctx.send("Data not found.")
    else:
        bank = bank[0]
        img = Image.new('RGB', background_image.size, color='white')
        img.paste(background_image, (0, 0))
        d = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        font = ImageFont.truetype("Swansea-q3pd.ttf", 60)
        text = f"{xp}"
        d.text((450, 220), text, fill='white', font=font)
        text = f"{bank}"
        d.text((425, 350), text, fill='white', font=font)
        user = ctx.author if user is None else user 

        pfp = user.avatar.url
        response = requests.get(pfp)
        if response.status_code == 200:
            pfp_content = response.content
            pfp_img = Image.open(io.BytesIO(pfp_content)).convert('RGB')
            pfp_img = ImageOps.fit(pfp_img, (64, 64), method=0, bleed=0.0, centering=(0.5, 0.5))


            mask = Image.new('L', (64, 64), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 64, 64), fill=255)

            pfp_img.putalpha(mask)


            img.paste(pfp_img, (800, 635), pfp_img)
        else:
            await ctx.send("Failed to fetch user's avatar.")
        username = user.name
        font = ImageFont.load_default()
        font= ImageFont.truetype("Swansea-q3pd.ttf", 45)
        d.text((900, 650), username, fill='white', font=font)
        image_buffer = io.BytesIO()
        img.save(image_buffer, format="PNG")
        image_buffer.seek(0)

        await ctx.send(file=discord.File(image_buffer, filename='balance_image.png'))


#------------------------------------------------------------------------------------


#rateninja
@bot.command(help="$rate - rates you or a person between 0 and 10")
async def rate(ctx,user_id): 

     rating = random.randint(0,10)
     await ctx.send(f"umm I rate {user_id} a {rating}/10!")

     if rating == 10:
      await ctx.send("u won 10 oreos for getting a 10/10")

      cursor.execute('UPDATE xp_data SET xp = + 10 ? WHERE user_id = ?', )


#give and take oreos 
memberss = {797057126707101716,864193768039120907}
@bot.command()
async def oreo(ctx, option, user: discord.User, amount: int,database):

  if ctx.author.id in memberss :
    if database == "wallet" :
      if (option == "add") :
        cursor.execute('INSERT OR IGNORE INTO xp_data (user_id) VALUES (?)', (user.id,))

        cursor.execute('UPDATE xp_data SET xp = xp + ? WHERE user_id = ?', (amount, user.id))
        connection.commit()

        await ctx.send(f"Added {amount} Oreos to {user.mention}'s wallet.")
      elif (option=="remove"):

         cursor.execute('INSERT OR IGNORE INTO xp_data (user_id) VALUES (?)', (user.id,))

         cursor.execute('UPDATE xp_data SET xp = xp - ? WHERE user_id = ?', (amount, user.id))
         connection.commit()


         await ctx.send(f"Taken {amount} Oreos from {user.mention}")

    elif database == "bank" :
      if (option == "add") :
        # Add the same amount to the bank
        cursor.execute('UPDATE xp_data SET bank = bank + ? WHERE user_id = ?', (amount, user.id))

        connection.commit()


        await ctx.send(f"Added {amount} Oreos to {user.mention}'s Bank")
      elif (option=="remove"):

         cursor.execute('INSERT OR IGNORE INTO xp_data (user_id) VALUES (?)', (user.id,))

         cursor.execute('UPDATE xp_data SET bank = bank - ? WHERE user_id = ?', (amount, user.id))
         connection.commit()


         await ctx.send(f"Taken {amount} Oreos from {user.mention}")

  else:
    await ctx.send("Only the bot user can use this command")

#------------------------------------------------------------------------------------



#coin
coin_usage = {}
@bot.command(help="$coin <heads or tails> <amount> , if u get the correct one u get that much oreos or loose")
async def coin(ctx, ht, amount):
    user_id = ctx.author.id 
    user_id = str(ctx.author.id)
    if user_id not in coin_usage:
      coin_usage[user_id] = {'count': 1, 'last_used': datetime.now()}
    else:
      user_data = coin_usage[user_id]
      user_data['count'] += 1

      if user_data['count'] >= 15:
          last_used = user_data['last_used']
          time_difference = datetime.now() - last_used
          if time_difference.total_seconds() < 86400:
              remaining_seconds = int(86400 - time_difference.total_seconds())
              hours, remainder = divmod(remaining_seconds, 3600)
              minutes, seconds = divmod(remainder, 60)
              remaining_time = f"{hours}h {minutes}m {seconds}s"
              embed = discord.Embed(
                  title=f"you can use the $coin command again in {remaining_time}",
                  #description=f"Sorry, you can use the $coin command again in {remaining_time}.",
                  color=0xFF0000  # Red color
              )
              await ctx.send(embed=embed)
              return

    cursor.execute('SELECT xp, level FROM xp_data WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()

    if user_data is None:
        await ctx.send("User data not found. Please create an account.")
        return

    user_balance = user_data[0]

    if int(amount) > user_balance:
        await ctx.send("Insufficient balance for this bet.")
        return
    random_heads_tails_generator = random.randint(0, 1) 

    landed = 'heads' if random_heads_tails_generator == 1 else 'tails'
    if ht == landed:
      user = ctx.author
      username = user.display_name
      user_avatar = user.avatar.url

      embed = discord.Embed(
          title=f"{username} ",
          description=f"💰You won {amount} oreo",
          color=0x00ff00
      )

      embed.set_thumbnail(url=user_avatar)


      embed.add_field(name="Game Details", value=f"🎲 | Landed {ht}\n🍪 | Bet {amount} oreo on {ht}", inline=False)

      await ctx.send(embed=embed)


      if ctx.author == bot.user:
          return

      user_id = str(ctx.author.id)

      cursor.execute("UPDATE xp_data SET xp = xp + ? WHERE user_id = ?", (amount, user_id))

      connection.commit()
    if ht != landed:
      if ctx.author == bot.user:
          return

      user = ctx.author
      username = user.display_name
      user_avatar = user.avatar.url

      embed = discord.Embed(
          title=f"{username} ",
          description=f"❌ You lost {amount} oreo",
          color=0xff0000 
        )

      embed.set_thumbnail(url=user_avatar)

      embed.add_field(name="Game Details", value=f"🎲 | Landed {landed}\n🍪 | Bet {amount} oreo on {ht}", inline=False)


      await ctx.send(embed=embed)
      user_id = ctx.author.id
      cursor.execute("UPDATE xp_data SET xp = xp - ? WHERE user_id = ?", (amount, user_id))

      connection.commit()

#------------------------------------------------------------------------------------



#shop
@bot.command()
async def shop(ctx):
    shop_items = {
    "rasengan" : 2000 ,
    "chidori"  : 4000 ,
    "steal" : 100000,
    "manufacturer" : 1000,

    }

    embed = discord.Embed(title="Oreo Tree Shop", description="Use $buy <item> to purchase a role!")
    for item, price in shop_items.items():
        embed.add_field(name=item, value=f"Price: {price} Oreos", inline=False)

    await ctx.send(embed=embed)


#buy command
@bot.command()
async def buy(ctx, item):
    shop_items = {
        "rasengan": 1000,
        "chidori": 1000,
        "steal": 100000,
        "manufacturer" : 1000,
        # Add more items here
    }

    user_id = str(ctx.author.id)

    if item.lower() in shop_items:
        price = shop_items[item.lower()]
        cursor.execute('SELECT bank FROM xp_data WHERE user_id = ?', (user_id,))
        user_bank_balance = cursor.fetchone()

        if user_bank_balance:
            user_bank_balance = user_bank_balance[0]

            if user_bank_balance >= price:
                cursor.execute('UPDATE xp_data SET bank = bank - ? WHERE user_id = ?', (price, user_id))
                connection.commit()

                role_name = item.lower()
                role = discord.utils.get(ctx.guild.roles, name=role_name)

                if role:
                    if role in ctx.author.roles:
                        await ctx.send(f"You already own the {item} role.")
                    else:
                        await ctx.author.add_roles(role)
                        await ctx.send(f"You have bought {item} for {price} Oreos. Enjoy your new role!")
                else:
                    await ctx.send("Sorry, there was an issue with the role. Please contact a moderator.")
            else:
                await ctx.send(f"Wd and try mb gonna fix Sorry, you don't have enough Oreos to buy {item}.")
        else:
            await ctx.send("User data not found.")
    else:
        await ctx.send(f"Sorry, {item} is not available in the shop.")

#------------------------------------------------------------------------------------

#Message
@bot.command()
@commands.has_any_role('『         ғᴏᴜɴᴅᴇʀ          』',)
async def mes(ctx, *, message_to_send):
      # Delete the user's command message
    await ctx.message.delete()


    await ctx.send(message_to_send)

@bot.command()
@commands.has_any_role('『         ғᴏᴜɴᴅᴇʀ          』','Mod')
async def message(ctx, *, message_to_send):
        # Delete the user's command message
    await ctx.message.delete()



    embed = discord.Embed(
      title=ctx.author.name,
     description=message_to_send,
  color=discord.Color.blue()  
)
    await ctx.send(embed=embed)


#------------------------------------------------------------------------------------

#snipe command
sniped_messages = {}
@bot.event
async def on_message_delete(message):
  sniped_messages[message.channel.id] = message
@bot.command(name='snipe', help='Show the last deleted message in the channel.')
async def snipe(ctx):
  channel_id = ctx.channel.id

  if channel_id in sniped_messages:
      deleted_message = sniped_messages[channel_id]
      author = deleted_message.author
      content = deleted_message.content
# 
      embed = discord.Embed(
          title=f'Deleted message by {author.display_name}',
          description=content,
          color=0xFF0000  # Red color
      )
      await ctx.send(embed=embed)
  else:
      await ctx.send('No deleted messages to snipe in this channel.')



#------------------------------------------------------------------------------------


#hug
@cooldown(1, 60, type=BucketType.user)
@bot.command(help='Send a virtual hug and happiness to a user')
async def hug(ctx, user: discord.User):

      hug_gif_url = 'https://shorturl.at/enVY8'
      happy_gif_url = 'https://shorturl.at/zRS29'

      initial_message = f'{ctx.author.display_name} just hugged {user.display_name}'
      pov_message = f'POV: {user.display_name} after that hug'

      await ctx.send(initial_message)

      hug_embed = discord.Embed()
      hug_embed.set_image(url=hug_gif_url)


      await ctx.send(embed=hug_embed)

      await ctx.send(pov_message)


      happy_embed = discord.Embed()
      happy_embed.set_image(url=happy_gif_url)


      await ctx.send(embed=happy_embed)


@hug.error
async def hug_error(ctx, error):
      if isinstance(error, commands.CommandOnCooldown):
          # Custom message when the command is on cooldown
          await ctx.send("Please wait a minute before doing that.")


#------------------------------------------------------------------------------------
#punch
@bot.command()
async def punch(ctx, user: discord.User, ):
      punch_gif_url1 = 'https://im5.ezgif.com/tmp/ezgif-5-259337410c.gif'
      punch_gif_url2 = 'https://im5.ezgif.com/tmp/ezgif-5-b8a0d18895.gif'
      punch_gif_url3 = 'https://shorturl.at/fqCF2'
      punch_gif_url4 = 'https://im5.ezgif.com/tmp/ezgif-5-3f5061635a.gif'
      x = random.randint(1,4)
      if x == 1:
        punch_gif_url = punch_gif_url1
      elif x == 2:
        punch_gif_url = punch_gif_url2
      elif x == 3:
        punch_gif_url = punch_gif_url3
      elif x == 4:
        punch_gif_url = punch_gif_url4


      message = f'{ctx.author.display_name} just punched {user.display_name}'
      await ctx.send(message)

      punch_embed = discord.Embed()
      punch_embed.set_image(url=punch_gif_url)

      await ctx.send(embed=punch_embed)   

#------------------------------------------------------------------------------------

total_oreos_stolen = {}
# Corrected $steal command
@bot.command(help="$steal <mention user> - Steal up to 1000 Oreos")

@commands.cooldown(1, 86400, commands.BucketType.user)
async def steal(ctx, target: discord.User):
    user_id = str(ctx.author.id)
    target_id = str(target.id)



    # Check if the user is trying to steal from themselves
    if user_id == target_id:
        await ctx.send("You can't steal from yourself.")
        return

    cursor.execute('SELECT xp FROM xp_data WHERE user_id = ?', (target_id,))
    target_data = cursor.fetchone()

    if target_data:
        target_balance = target_data[0]

        if target_balance >= 1000:
            max_steal = min(1000, target_balance)

            if max_steal > 0:
                # Calculate the amount to steal (random value between 1 and max_steal)

                amount_stolen = random.randint(1,max_steal)

                # Deduct the stolen Oreos 
                cursor.execute('UPDATE xp_data SET xp = xp - ? WHERE user_id = ?', (amount_stolen, target_id))

                # Add the stolen Oreos to the user's balance
                cursor.execute('UPDATE xp_data SET xp = xp + ? WHERE user_id = ?', (amount_stolen, user_id))

                # Update the total Oreos stolen by the user
                if user_id in total_oreos_stolen:
                    total_oreos_stolen[user_id] += amount_stolen
                else:
                    total_oreos_stolen[user_id] = amount_stolen

                # Check if the user reached a total of 1000 Oreos stolen
                if total_oreos_stolen[user_id] >= 1000:
                    await ctx.send("You have reached 1000 Oreos stolen. You have a 1-day cooldown.")
                    total_oreos_stolen[user_id] = 0  # Reset the total stolen Oreos

                # Send an embedded message with the result
                embed = discord.Embed(title="" , description=f"You have stolen {amount_stolen} Oreos from <@{target_id}>.", color=0x4d94ff)
                embed.set_author(name='Oreos Stolen', icon_url=f'{ctx.author.avatar.url}')
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"{target.mention} doesn't have enough Oreos to steal.")
        else:
            await ctx.send(f"{target.mention} doesn't have enough Oreos to steal.")
    else:
        await ctx.send("User data not found.")

# Handle cooldown error for the $steal command
@steal.error
async def steal_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        retry_after = round(error.retry_after / 3600)  # Convert seconds to hours
        await ctx.send(f"You are on cooldown for the $steal command. Try again in {retry_after} hours.")

#------------------------------------------------------------------------------------



@bot.command(help='Use $dep <amount or "all"> to deposit Oreos into the bank.')
async def dep(ctx, amount: Union[str, int]):
    user_id = str(ctx.author.id)

    # Check if the user has a balance in xp_data.db
    cursor.execute('SELECT xp FROM xp_data WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        user_balance = user_data[0]

        if amount.lower() == "all":
            if user_balance > 0:
                # Deposit the entire wallet balance to the bank
                cursor.execute('UPDATE xp_data SET xp = xp - ? WHERE user_id = ?', (user_balance, user_id))
                cursor.execute('UPDATE xp_data SET bank = bank + ? WHERE user_id = ?', (user_balance, user_id))
                connection.commit()
                cursor.execute('SELECT xp FROM xp_data WHERE user_id = ?', (user_id,))
                user_bal = cursor.fetchone()[0]
                cursor.execute('SELECT bank FROM xp_data WHERE user_id = ?',(user_id,))
                bank_balance = cursor.fetchone()[0]

                embed = discord.Embed(
                  title=ctx.author.display_name,
                  description=f"💳 | Wallet: {user_bal} Oreos\n🏦 | Bank: {bank_balance} Oreos",
                  color=ctx.author.color  
                )

                # Add the user's avatar to the right side
                embed.set_thumbnail(url=ctx.author.avatar.url)

                embed.add_field(name="Deposite", value=f"You have deposited {user_balance} Oreos to your wallet.")

                await ctx.send(embed=embed)
            else:
                await ctx.send("Your wallet is empty. There's nothing to deposit.")
        elif str(amount).isdigit() and int(amount) > 0:
            deposit_amount = int(amount)
            if deposit_amount <= user_balance:
                # Deposit the specified amount from the user's balance
                cursor.execute('UPDATE xp_data SET xp = xp - ? WHERE user_id = ?', (deposit_amount, user_id))
                cursor.execute('UPDATE xp_data SET bank = bank + ? WHERE user_id = ?', (deposit_amount, user_id))
                connection.commit()

                cursor.execute('SELECT xp FROM xp_data WHERE user_id = ?', (user_id,))
                user_balance = cursor.fetchone()[0]
                cursor.execute('SELECT bank FROM xp_data WHERE user_id = ?', (user_id,))
                bank_balance = cursor.fetchone()[0]

                embed = discord.Embed(
                  title=ctx.author.display_name,
                  description=f"💳 | Wallet: {user_balance} Oreos\n🏦 | Bank: {bank_balance} Oreos",
                  color=ctx.author.color  
                )

                # Add the user's avatar to the right side
                embed.set_thumbnail(url=ctx.author.avatar.url)

                embed.add_field(name="Deposite", value=f"You have deposited {amount} Oreos to your wallet.")

                await ctx.send(embed=embed)
            else:
                await ctx.send("You don't have enough Oreos to deposit that amount.")
        else:
            await ctx.send("Invalid input. Please enter a valid amount or 'all'.")
    else:
        await ctx.send("User data not found.")

#------------------------------------------------------------------------------------


#wd command
@bot.command(help='Use $wd <amount> to deposit Oreos into the bank.')
async def wd(ctx, amount: int):
    user_id = str(ctx.author.id)

    # Check if the user has a balance in xp_data.db
    cursor.execute('SELECT xp FROM xp_data WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        user_balance = user_data[0]

    cursor.execute('SELECT bank FROM xp_data WHERE user_id = ?', (user_id,))
    user_bank = cursor.fetchone()
    if user_bank:
        user_bank = user_bank[0]
        if amount <= 0:
            await ctx.send("Please enter a valid amount to withdraw.")
        elif amount > user_bank:
            await ctx.send("You don't have enough Oreos to withdraw.")
        else:
            # Deduct the amount from the user's balance
            cursor.execute('UPDATE xp_data SET bank = bank - ? WHERE user_id = ?', (amount, user_id))

            # Add the same amount to the bank
            cursor.execute('UPDATE xp_data SET xp = xp + ? WHERE user_id = ?', (amount,user_id ))

            connection.commit()
            cursor.execute('SELECT bank FROM xp_data WHERE user_id = ?', (user_id,))
            bank_balance = cursor.fetchone()[0]

            embed = discord.Embed(
              title=ctx.author.display_name,
              description=f"💳 | Wallet: {user_balance + amount} Oreos\n🏦 | Bank: {bank_balance} Oreos",
              color=0x000000  # Black color
            ) #lol

            # Add the user's avatar to the right side
            embed.set_thumbnail(url=ctx.author.avatar.url)

            embed.add_field(name="Withdraw", value=f"You have Withdraw {amount} Oreos to your wallet.")

            await ctx.send(embed=embed)

    else:
        await ctx.send("User data not found.")


#------------------------------------------------------------------------------------


@bot.command(help='Display your cooldowns')
async def cd(ctx):
    str(ctx.author.id)
    cooldowns_info = []

    for command in bot.walk_commands():
        if command.name != 'hug' and command._buckets._cooldown:
            remaining_time = await command._buckets.get_bucket(ctx.message).get_retry_after(ctx)
            cooldowns_info.append(f'{command.name}: {round(remaining_time)} seconds')

    if cooldowns_info:
        await ctx.send('\n'.join(cooldowns_info))
    else:
        await ctx.send('You have no cooldowns for other commands.')

MEME_API_URL = "https://memegen.link/api/"
@bot.command(help="$meme - Fetch and display a random meme")
async def meme(ctx):
    try:
        # Send a request to the meme API
        response = requests.get(MEME_API_URL)
        meme_data = response.json()

        if "url" in meme_data:
            meme_url = meme_data["url"]

            # Create an embedded message with the meme image
            embed = discord.Embed(title="Random Meme", color=0x4d94ff)
            embed.set_image(url=meme_url)

            # Send the embedded message to the channel
            await ctx.send(embed=embed)
        else:
            await ctx.send("Sorry, I couldn't fetch a meme at the moment.")
    except Exception as e:
        print(e)
        await ctx.send("An error occurred while fetching the meme. Please try again later.")


#------------------------------------------------------------------------------------


@bot.command()
async def idk(ctx):

  embed = discord.Embed(title="Even idk dude", description='', color=0x428579)
  embed.set_image(url="https://shorturl.at/hlmFV") 

  await ctx.send(embed=embed)


@bot.command(help='Use $wd <amount> to deposit Oreos into the bank.')
async def spoof(ctx, user: discord.User ):
    str(ctx.author.id)

    embed = discord.Embed(title="Even idk dude", description='', color=0x428579)


    await ctx.send(embed=embed)
@bot.command()
async def rasenmeow(ctx): 
  embed = discord.Embed(title="Rasenmeow", description='', color=0x428579)

  embed.set_image(url="https://shorturl.at/cnqYZ")
  await ctx.send(embed=embed)


#------------------------------------------------------------------------------------

#music command
@bot.command()
async def play(ctx, *, query):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }

        async def get_audio_url(query):
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(f"ytsearch:{query}", download=False)
                    if 'entries' in info:
                        return info['entries'][0]['url']
                    else:
                        return info['url']
                except Exception as e:
                    print(e)
                    return None

        URL = query if query.startswith('http') else await get_audio_url(query)

        if URL:
            voice_client.play(discord.FFmpegPCMAudio(URL))
        else:
            await ctx.send("No audio found.")
    else:
        await ctx.send("You are not in a voice channel.")
@bot.command()
async def stop(ctx):
  voice_client = ctx.voice_client

  if voice_client.is_playing():
      voice_client.stop()

  await voice_client.disconnect()


keep_alive.keep_alive()
bot.run(KEY)