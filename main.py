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
import yt_dlp
from discord.ext import commands
from discord.ext.commands import BucketType, cooldown
from PIL import Image, ImageDraw, ImageFont, ImageOps
import platform
import psutil
import keep_alive
from character import character_images
from op_characters import character_images_op
import os
from dotenv import load_dotenv
import opuslib
import math

load_dotenv()

KEY = os.getenv('TOKEN') 
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

#daily

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

        embed = discord.Embed(
            title="⏳ Daily Reward Cooldown",
            description=f"You can claim your next daily reward in `{remaining_hours}` hours `{remaining_minutes}` minutes.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Come back later for more Oreos!")
        await ctx.send(embed=embed)

    else:
        reward = random.randint(250, 350)
        cursor.execute('INSERT OR IGNORE INTO xp_data (user_id) VALUES (?)', (user_id,))
        cursor.execute('UPDATE xp_data SET xp = xp + ? WHERE user_id = ?', (reward, user_id))
        connection.commit()
        daily_cooldowns[user_id] = datetime.now()

        embed = discord.Embed(
            title="🎉 Daily Reward Claimed!",
            description=f"Congratulations! You earned `{reward} Oreos` today.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Enjoy your Oreos and come back tomorrow for more!")
        await ctx.send(embed=embed)

@daily.error
async def daily_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        remaining_time = error.retry_after
        remaining_hours, remainder = divmod(remaining_time, 3600)
        remaining_minutes, _ = divmod(remainder, 60)

        embed = discord.Embed(
            title="⏳ Daily Reward Cooldown",
            description=f"You are on cooldown. Try again in `{int(remaining_hours)}` hours `{int(remaining_minutes)}` minutes.",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Patience is key! More Oreos coming soon!")
        await ctx.send(embed=embed)


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
@commands.has_any_role('『         ғᴏᴜɴᴅᴇʀ          』', 'Mod')
async def msgdel(ctx, amount: int):
  if amount == 0:
    await ctx.send('Invalid amount!')
    return 

  await ctx.channel.purge(limit=amount + 1)

@msgdel.error
async def msgdel_error(ctx, error):
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
            time_difference = current_time - datetime.fromisoformat(last_played)
            if time_difference.days >= 1:
                user_game_count = 0

        user_game_count += 1
        cursor.execute('UPDATE xp_data SET user_game_count = ?, last_played = ? WHERE user_id = ?',
                       (user_game_count, current_time.isoformat(), user_id))
    else:
        user_game_count = 1
        cursor.execute('INSERT INTO xp_data (user_id, user_game_count, last_played) VALUES (?, ?, ?)',
                       (user_id, user_game_count, current_time.isoformat()))

    connection.commit()

    if user_game_count > daily_game_limit:
        embed = discord.Embed(
            title="🚫 Daily Limit Reached",
            description="You've reached the daily game limit. Try again tomorrow!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    correct_reward = random.randint(19, 32)
    allowed_channel_id = [1166294561300168735, 1166473829195984977, 1166473801056387163]
    if ctx.channel.id not in allowed_channel_id:
        embed = discord.Embed(
            title="❌ Wrong Channel",
            description="This command can only be used in Oreo chats.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    character_data = character_images_op if option == 'op' else character_images
    character_entry = random.choice(list(character_data.items()))
    character_name = character_entry[0]
    alternative_names = character_entry[1]['names']
    image_url = character_entry[1]['image']

    embed = discord.Embed(title="🕵️‍♂️ Character Guessing Game", color=discord.Color.blue())
    embed.set_image(url=image_url)
    embed.set_footer(text="You have 3 attempts! Type the character name to guess.")
    await ctx.send(embed=embed)

    def check(message):
        return message.author == ctx.author

    attempts = 3
    while attempts > 0:
        try:
            user_guess = await bot.wait_for('message', timeout=15, check=check)
            guess = user_guess.content.strip().lower()

            if guess in [name.lower() for name in alternative_names]:
                cursor.execute('UPDATE xp_data SET xp = xp + ? WHERE user_id = ?', (correct_reward, user_id))
                connection.commit()

                games_left = max(0, daily_game_limit - user_game_count)
                embed = discord.Embed(
                    title="🎉 Correct!",
                    description=f"💰 You won **{correct_reward}** Oreos!",
                    color=discord.Color.green()
                )
                embed.add_field(name="✅ Possible Answers", value=f"**{character_name}**", inline=False)
                embed.add_field(name="🎮 Games Remaining", value=f"`{games_left}` games left today", inline=False)
                await ctx.send(embed=embed)
                return
            else:
                attempts -= 1
                if attempts > 0:
                    embed = discord.Embed(
                        title="❌ Wrong Answer",
                        description=f"Try again! You have `{attempts}` attempts left.",
                        color=discord.Color.orange()
                    )
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="❌ Game Over!",
                        description="You have no more attempts left.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="✅ Correct Answer", value=f"**{character_name}**", inline=False)
                    await ctx.send(embed=embed)
                    return

        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏳ Time's Up!",
                description="You took too long to respond.",
                color=discord.Color.red()
            )
            embed.add_field(name="✅ Correct Answer was", value=f"**{character_name}**", inline=False)
            await ctx.send(embed=embed)
            return


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
  embed.set_footer(text='Type the character name to guess. \nYou got 15 seconds on the clock')

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

#Leadboard
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import math

@bot.command(name='lb', help="$lb to see the leaderboard of Oreos, use $lb <page> for more pages")
async def leaderboard(ctx, page: int = 1):
    per_page = 9  # Users per page
    try:
        cursor.execute('SELECT user_id, xp, bank FROM xp_data ORDER BY (xp + bank) DESC')
        all_users = cursor.fetchall()
    except Exception as e:
        await ctx.send(f"Database error: {e}")
        return

    if not all_users:
        await ctx.send("No leaderboard data available.")
        return

    total_pages = math.ceil(len(all_users) / per_page)
    if page < 1 or page > total_pages:
        await ctx.send(f"Invalid page! Choose between 1 and {total_pages}.")
        return

    start_index = (page - 1) * per_page
    top_users = all_users[start_index:start_index + per_page]

    img_width, img_height = 1500, 1900
    img = Image.new('RGB', (img_width, img_height), color=(12, 16, 21))
    d = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("Swansea-q3pd.ttf", 90)
        font = ImageFont.truetype("Swansea-q3pd.ttf", 70)
    except IOError:
        await ctx.send("Font file missing! Please ensure 'Swansea-q3pd.ttf' is available.")
        return

    trophy_url = "https://i.postimg.cc/x1JDJgHn/trophy.png"
    try:
        trophy_response = requests.get(trophy_url)
        trophy_icon = Image.open(io.BytesIO(trophy_response.content)).convert("RGBA").resize((120, 120))
    except Exception:
        await ctx.send("Failed to load trophy image.")
        return

    title_text = "Oreo Leaderboard"
    text_width = d.textbbox((0, 0), title_text, font=title_font)[2]
    title_x = (img_width - text_width) // 2
    title_y = 100

    trophy_x_left = title_x - 150
    trophy_x_right = title_x + text_width + 40
    trophy_y = title_y - 30

    img.paste(trophy_icon, (trophy_x_left, trophy_y), trophy_icon)
    img.paste(trophy_icon, (trophy_x_right, trophy_y), trophy_icon)

    d.text((title_x, title_y), title_text, fill='white', font=title_font)

    y_offset = 250
    user_rank = next((rank for rank, (uid, _, _) in enumerate(all_users, start=1) if uid == ctx.author.id), None)

    for i, (user_id, xp, bank) in enumerate(top_users, start=start_index + 1):
        user = ctx.guild.get_member(user_id) or await bot.fetch_user(user_id)
        if not user:
            continue

        total_oreos = xp + bank
        d.text((80, y_offset), f"#{i} {user.name}", fill='white', font=font)
        d.text((200, y_offset + 85), f"{total_oreos:,} Oreos", fill='gold', font=font)
        y_offset += 180

    image_buffer = io.BytesIO()
    img.save(image_buffer, format="PNG")
    image_buffer.seek(0)

    embed = discord.Embed(title="Oreo Leaderboard", color=discord.Color.gold())
    embed.set_image(url="attachment://leaderboard.png")
    embed.set_footer(text=f"Page {page}/{total_pages} • Your Rank: {user_rank if user_rank else 'Unranked'}")
    embed.set_author(name=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    await ctx.send(file=discord.File(image_buffer, filename='leaderboard.png'), embed=embed)


  #-----------------------------------------------------------------------------------


#bal

@bot.command(name='bal', help="$bal to see how many Oreos you have")
async def bal(ctx, user: discord.User = None):
    background_url = 'https://c4.wallpaperflare.com/wallpaper/7/670/485/line-multi-colored-black-background-wallpaper-preview.jpg'
    background_response = requests.get(background_url)
    background_image = Image.open(io.BytesIO(background_response.content))

    user_id = ctx.author.id if user is None else user.id

    cursor.execute('SELECT xp, level, bank FROM xp_data WHERE user_id = ?', (user_id,))
    data = cursor.fetchone()

    if data is None:
        await ctx.send("User data not found.")
    else:
        xp, level, bank = data

        img = Image.new('RGB', background_image.size, color='white')
        img.paste(background_image, (0, 0))
        d = ImageDraw.Draw(img)
        wallet_font = ImageFont.truetype("arial.ttf", 34)
        bank_font = ImageFont.truetype("Swansea-q3pd.ttf", 35)

        wallet_icon_url = "https://i.postimg.cc/QtHyrgKn/image.png"
        bank_icon_url = "https://cdn-icons-png.freepik.com/256/8176/8176383.png"

        wallet_icon_response = requests.get(wallet_icon_url)
        wallet_icon = Image.open(io.BytesIO(wallet_icon_response.content)).convert("RGBA")
        wallet_icon = wallet_icon.resize((55, 65))

        bank_icon_response = requests.get(bank_icon_url)
        bank_icon = Image.open(io.BytesIO(bank_icon_response.content)).convert("RGBA")
        bank_icon = bank_icon.resize((40, 40))

        wallet_text = f"Wallet : {xp:,} Oreos"
        bank_text = f"Bank : {bank:,} Oreos"

        
        d.text((100, 100), wallet_text, fill='white', font=wallet_font)
        d.text((100, 160), bank_text, fill='white', font=bank_font)

        img.paste(wallet_icon, (40,80), wallet_icon)
        img.paste(bank_icon, (50, 155), bank_icon)

        user = ctx.author if user is None else user
        pfp = user.avatar.url
        response = requests.get(pfp)

        if response.status_code == 200:
            pfp_content = response.content
            pfp_img = Image.open(io.BytesIO(pfp_content)).convert('RGB')
            pfp_img = ImageOps.fit(pfp_img, (80, 80), method=0, bleed=0.0, centering=(0.5, 0.5))

            mask = Image.new('L', (80, 80), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 80, 80), fill=255)
            pfp_img.putalpha(mask)

            img_width, img_height = img.size
            pfp_x = img_width - 110
            pfp_y = img_height - 130  # Move PFP slightly up

            img.paste(pfp_img, (pfp_x, pfp_y), pfp_img)
        else:
            await ctx.send("Failed to fetch user's avatar.")
            return

        username = user.name
        font = ImageFont.truetype("arial.ttf", 30)
        text_bbox = d.textbbox((0, 0), username, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        img_width, _ = img.size

        text_x = (img_width - text_width) / 2
        text_y = 20  # Keep it at the same height

        # Draw the username
        d.text((text_x, text_y), username, fill='white', font=font)

        # Draw the underline
        underline_y = text_y + text_height + 5  # Slightly below the text
        d.line((text_x, underline_y, text_x + text_width, underline_y), fill='white', width=2)


        # Add display name below the profile picture
        display_name = user.display_name
        font_display = ImageFont.truetype("arial.ttf", 25)
        text_bbox = d.textbbox((0, 0), display_name, font=font_display)
        text_width = text_bbox[2] - text_bbox[0]

        text_x = pfp_x + (80 - text_width) // 2  # Center text under PFP
        text_y = pfp_y  + 95  # Just below the PFP

        d.text((text_x, text_y), display_name, fill='white', font=font_display)

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
memberss = {797057126707101716,864193768039120907,}
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
    """Plays a song from JioSaavn."""
    if not ctx.author.voice:
        return await ctx.send("You need to be in a voice channel first!")

    vc = ctx.voice_client
    if not vc:
        vc = await ctx.author.voice.channel.connect()

    # Search for the song
    search_url = f"https://jio-saavan-api-gold.vercel.app//search?query={query}"
    response = requests.get(search_url).json()

    if not response or "data" not in response or not response["data"]:
        return await ctx.send("No results found!")

    song = response["data"][0]  # Get the first result
    song_title = song["title"]
    song_id = song["id"]

    # Get the song URL
    song_url = f"https://jio-saavan-api-gold.vercel.app//song?id={song_id}"
    song_response = requests.get(song_url).json()

    if "data" not in song_response or "media_url" not in song_response["data"]:
        return await ctx.send("Couldn't fetch the song URL!")

    stream_url = song_response["data"]["media_url"]

    # Play the song
    vc.stop()
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    audio_source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)
    vc.play(audio_source)

    await ctx.send(f"🎵 Now playing: {song_title}")

@bot.command()
async def stop(ctx):
    """Stops and disconnects the bot."""
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()


keep_alive.keep_alive()
bot.run(KEY)