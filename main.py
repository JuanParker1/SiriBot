import discord, datetime, time
from discord.ext import commands, tasks
from itertools import cycle
import random
import json
from time import sleep
from datetime import *
from discord_components import *
from discord.utils import get
import os
import math
import os_utils
import os
import logging
import asyncio
from pathlib import Path
from discord.ext import commands
from discord_components import InteractionType
import aiosqlite
import asyncio

intents = discord.Intents().all()
client = commands.Bot(command_prefix='?', intents=intents)
client.remove_command("help")

status = cycle(
    ['Hello! Im Siri-Bot', 'Type !help to know!', 'Bot by Shreyas-ITB'])


@client.event
async def on_ready():
    change_status.start()
    print('Bot is ready')
    DiscordComponents(client)


@tasks.loop(seconds=3)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


####################################################################
####################################################################
# Main code starts :)

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! Showing the bot reply latency... currently at {round(client.latency * 1000)}ms')      


@client.command(aliases=['bal'])
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author

    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(title=f'{ctx.author.name} Balance', color=discord.Color.green())
    em.add_field(name="Wallet Balance", value=wallet_amt)
    em.add_field(name="Bank Balance", value=bank_amt)
    await ctx.send(embed=em)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = '**Still on CoolDown**, Please try again in {:.2f}s out of 24hours..'.format(error.retry_after)
        await ctx.send(msg)


@client.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def claim(ctx):
    await open_account(ctx.author)
    user = ctx.author

    users = await get_bank_data()

    earnings = random.randrange(80)

    await ctx.send(f'{ctx.author.mention} Got {earnings} coins!!')

    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json", 'w') as f:
        json.dump(users, f)


@client.command(aliases=['wd'])
async def withdraw(ctx, amount=None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[1]:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return

    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1 * amount, 'bank')
    await ctx.send(f'{ctx.author.mention} You withdrew {amount} coins')


@client.command(aliases=['dp'])
async def deposit(ctx, amount=None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return

    await update_bank(ctx.author, -1 * amount)
    await update_bank(ctx.author, amount, 'bank')
    await ctx.send(f'{ctx.author.mention} You deposited {amount} coins')


@client.command(aliases=['sm'])
async def send(ctx, member: discord.Member, amount=None):
    await open_account(ctx.author)
    await open_account(member)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)
    if amount == 'all':
        amount = bal[0]

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return

    await update_bank(ctx.author, -1 * amount, 'bank')
    await update_bank(member, amount, 'bank')
    await ctx.send(f'{ctx.author.mention} You gave {member} {amount} coins')


async def open_account(user):
    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open('mainbank.json', 'w') as f:
        json.dump(users, f)

    return True


async def get_bank_data():
    with open('mainbank.json', 'r') as f:
        users = json.load(f)

    return users


async def update_bank(user, change=0, mode='wallet'):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open('mainbank.json', 'w') as f:
        json.dump(users, f)
    bal = users[str(user.id)]['wallet'], users[str(user.id)]['bank']
    return bal

id = 859368295823835136

@client.command()
async def gstart(ctx, time=None, * , prize):
    if ctx.author.id == id:
        if time == None:
            return await ctx.send("Please include the time!")
        elif prize == None:
            return await ctx.send("Please include the giveaway price!")
        await ctx.send("YO! Guys!! Come here..")
        embed1 = discord.Embed(title="New Giveaway!!! 🎉🎉🎉", description=f"""Giveaway Hosted By {ctx.author.mention} is Givingaway
        **{prize}coins!! ** Go React with 🎉 icon and enter the giveaway Now! Cheers everyone!!!!""")
        time_convert = {"s": 1, "m": 60, "h": 3600, 'd': 86400}
        gawtime = int(time[0]) * time_convert[time[-1]]
        embed1.set_footer(text=f"Giveaway ends in {time}")
        gaw_msg = await ctx.send(embed=embed1)
        await gaw_msg.add_reaction("🎉")
        await asyncio.sleep(gawtime)
        new_gaw_message = await ctx.channel.fetch_message(gaw_msg.id)
        users = await new_gaw_message.reactions[0].users().flatten()
        users.pop(users.index(client.user))
        winner = random.choice(users)
        await ctx.send(f"YAY!! {winner.mention} has won the giveaway for **{prize} coin(s)** GG!!!")
        await ctx.send(f"{winner.mention} Please Contact {ctx.author.mention} for Your Giveaway Reward!! Thankyou")
    else:
        await ctx.send("**ERROR:** ID Doesnt MATCH! You Dont Have Permissions To Host Giveaways!!!.")

@client.command()
@commands.is_owner()
async def setclear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)

@client.command()
async def vsiri(ctx):
    e = discord.Embed(title="About vSiri!", colour=discord.Colour.green())
    e.add_field(name="What is VSiri??", value="""
    vSiri Stands for Virtual Siri coins given by Siri-Bot,
    there is no crypto called vSiri coins but, these are virtual coins something you can earn in discord
    and can be exchanged with Siri Coins Awesome right!!. Bot coins are also called as vSiri!!, Now To get started just do !bal to check your balance 
    first then claim ur coins by !claim then if you want additional features refer !help""")
    await ctx.send(embed=e)


@client.command()
async def about(ctx):
    newem = discord.Embed(title="About Siri-Bot:", colour=discord.Colour.gold())
    newem.add_field(name="Description:", value="""
    Nothing to show Yet""")
    await ctx.send(embed=newem)

id = 859368295823835136

@client.command()
async def shutdown(ctx):
    if ctx.author.id == id:
        try:
           await ctx.send("Shutdown Recieved!!")
           sleep(3)
           await ctx.send("Saving Coin Data..")
           sleep(3)
           await ctx.send("Closing Commands..")
           sleep(3)
           await ctx.send("No errors Detected... Shutting the bot down...")
           await ctx.bot.logout()
        except:
            await ctx.send("Shutdown Recieved!!")
            sleep(3)
            await ctx.send("ERROR Encountered..You cant shut the bot down..")
            sleep(3)
            await ctx.send(f"{ctx.author.mention}ADMIN previlages Required to shut GLM GOD down!!")
    else:
        await ctx.send("**ERROR:** You Dont Have Permissions To ShutMe Down!!!.")

async def update_totals(member):
    invites = await member.guild.invites()

    c = datetime.today().strftime("%Y-%m-%d").split("-")
    c_y = int(c[0])
    c_m = int(c[1])
    c_d = int(c[2])

    async with client.db.execute("SELECT id, uses FROM invites WHERE guild_id = ?", (member.guild.id,)) as cursor: # this gets the old invite counts
        async for invite_id, old_uses in cursor:
            for invite in invites:
                if invite.id == invite_id and invite.uses - old_uses > 0: # the count has been updated, invite is the invite that member joined by
                    if not (c_y == member.created_at.year and c_m == member.created_at.month and c_d - member.created_at.day < 7): # year can only be less or equal, month can only be less or equal, then check days
                        print(invite.id)
                        await client.db.execute("UPDATE invites SET uses = uses + 1 WHERE guild_id = ? AND id = ?", (invite.guild.id, invite.id))
                        await client.db.execute("INSERT OR IGNORE INTO joined (guild_id, inviter_id, joiner_id) VALUES (?,?,?)", (invite.guild.id, invite.inviter.id, member.id))
                        await client.db.execute("UPDATE totals SET normal = normal + 1 WHERE guild_id = ? AND inviter_id = ?", (invite.guild.id, invite.inviter.id))

                    else:
                        await client.db.execute("UPDATE totals SET normal = normal + 1, fake = fake + 1 WHERE guild_id = ? and inviter_id = ?", (invite.guild.id, invite.inviter.id))

                    return
    
# events
@client.event
async def on_member_join(member):
    await update_totals(member)
    await client.db.commit()
    client.process_commands(message)
        
@client.event
async def on_member_remove(member):
    cur = await client.db.execute("SELECT inviter_id FROM joined WHERE guild_id = ? and joiner_id = ?", (member.guild.id, member.id))
    res = await cur.fetchone()
    client.process_commands(message)
    if res is None:
        return
    
    inviter = res[0]
    
    await client.db.execute("DELETE FROM joined WHERE guild_id = ? AND joiner_id = ?", (member.guild.id, member.id))
    await client.db.execute("DELETE FROM totals WHERE guild_id = ? AND inviter_id = ?", (member.guild.id, member.id))
    await client.db.execute("UPDATE totals SET left = left + 1 WHERE guild_id = ? AND inviter_id = ?", (member.guild.id, inviter))
    await client.db.commit()

@client.event
async def on_invite_create(invite):
    await client.db.execute("INSERT OR IGNORE INTO totals (guild_id, inviter_id, normal, left, fake) VALUES (?,?,?,?,?)", (invite.guild.id, invite.inviter.id, invite.uses, 0, 0))
    await client.db.execute("INSERT OR IGNORE INTO invites (guild_id, id, uses) VALUES (?,?,?)", (invite.guild.id, invite.id, invite.uses))
    await client.db.commit()
    client.process_commands(message)
    
@client.event
async def on_invite_delete(invite):
    await client.db.execute("DELETE FROM invites WHERE guild_id = ? AND id = ?", (invite.guild.id, invite.id))
    await client.db.commit()
    client.process_commands(message)

@client.event
async def on_guild_join(guild): # add new invites to monitor
    for invite in await guild.invites():
        await client.db.execute("INSERT OR IGNORE INTO invites (guild_id, id, uses), VAlUES (?,?,?)", (guild.id, invite.id, invite.uses))
        client.process_commands(message)
    await client.db.commit()
    
@client.event
async def on_guild_remove(guild): # remove all instances of the given guild_id
    await client.db.execute("DELETE FROM totals WHERE guild_id = ?", (guild.id,))
    await client.db.execute("DELETE FROM invites WHERE guild_id = ?", (guild.id,))
    await client.db.execute("DELETE FROM joined WHERE guild_id = ?", (guild.id,))
    client.process_commands(message)
    await client.db.commit()
    
# commands
@client.command()
async def invites(ctx, member: discord.Member=None):
    if member is None: member = ctx.author

    # get counts
    cur = await client.db.execute("SELECT normal, left, fake FROM totals WHERE guild_id = ? AND inviter_id = ?", (ctx.guild.id, member.id))
    res = await cur.fetchone()
    if res is None:
        normal, left, fake = 0, 0, 0

    else:
        normal, left, fake = res
        user = ctx.author
        users = await get_bank_data()
        earnings = 50
        users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json", 'w') as f:
        json.dump(users, f)

    total = normal - (left + fake)
    await ctx.send(f"You Have Got {earnings} coins just for inviting your friend!! Invite More to earn More!")
    
    em = discord.Embed(
        title=f"Invites for {member.name}#{member.discriminator}",
        description=f"{member.mention} currently has **{total}** invites. (**{normal}** normal, **{left}** left, **{fake}** fake).",
        timestamp=datetime.now(),
        colour=discord.Colour.orange())

    await ctx.send(embed=em)
    
async def setup():
    await client.wait_until_ready()
    client.db = await aiosqlite.connect("inviteData.db")
    await client.db.execute("CREATE TABLE IF NOT EXISTS totals (guild_id int, inviter_id int, normal int, left int, fake int, PRIMARY KEY (guild_id, inviter_id))")
    await client.db.execute("CREATE TABLE IF NOT EXISTS invites (guild_id int, id string, uses int, PRIMARY KEY (guild_id, id))")
    await client.db.execute("CREATE TABLE IF NOT EXISTS joined (guild_id int, inviter_id int, joiner_id int, PRIMARY KEY (guild_id, inviter_id, joiner_id))")
    
    # fill invites if not there
    for guild in client.guilds:
        for invite in await guild.invites(): # invites before bot was added won't be recorded, invitemanager/tracker don't do this
            await client.db.execute("INSERT OR IGNORE INTO invites (guild_id, id, uses) VALUES (?,?,?)", (invite.guild.id, invite.id, invite.uses))
            await client.db.execute("INSERT OR IGNORE INTO totals (guild_id, inviter_id, normal, left, fake) VALUES (?,?,?,?,?)", (guild.id, invite.inviter.id, 0, 0, 0))
                                 
    await client.db.commit()

client.loop.create_task(setup())

@client.command()
async def contribute(ctx):
    em = discord.Embed(title="Contribute  for the bot!!", colour=discord.Colour.green())
    em.add_field(name="Contribute Addresses:", value="""
    Addresses are on their way!!
    Thanks for the contribution!! we are even happy for the smallest transaction that you have just made!! it will e useful..""")
    em.add_field(name="Donate For Shreyas-ITB", value="""
    """)
    await ctx.send(embed=em)

@client.command()
@commands.guild_only()
@commands.is_owner()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    embed = discord.Embed(title="Kick Command Used By The Mods!!", description=f"""
    **A Member/Bot Named ```{member}``` Has Beed Kicked From the Guild/server Due To Reason:**
    ```{reason}```
    Kicked By ```{ctx.author.name}```""", colour=discord.Colour.red())
    await ctx.send(embed=embed)

@client.command()
@commands.is_owner()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    embed = discord.Embed(title="Ban Command Used By The Mods!!", description=f"""
    **A Member/Bot Named ```{member}``` Has Beed Banned From the Guild/server Due To Reason:**
    ```{reason}```
    Banned By ```{ctx.author.name}```""", colour=discord.Colour.red())
    await ctx.send(embed=embed)

@client.command()
@commands.is_owner()
async def unban(ctx, * , member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator =member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"Unbanned {user.mention}")
            return

@client.command(aliases=['fb'])
async def feedback(ctx, *, data):
    with open("feedback.txt", "w") as file1:
        print(f"{ctx.author.name} has posted his/her feedback: {data}")
    await ctx.send(
        f"{ctx.author.mention} Your Bug or issue/feedback has been noted Thankyou.. Shreyas Will reach you soon.")

@client.command(aliases=["lb"])
async def leaderboard(ctx, x=10):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total, reverse=True)

    em = discord.Embed(title=f"Top {x} Richest People ",
                       description="This is decided on the basis of raw money in the bank and wallet",
                       color=discord.Color.gold())
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = ctx.guild.get_member(id_)
        name = member.display_name
        em.add_field(name=f"{index}. {name}", value=f"{amt}", inline=False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed=em)

page1 = discord.Embed(title="General Help Commands!:", description="""
    **?invites**(The Reward is Experimental) Adds your ID in the database, tracks your invite and gives you vSiri.
    **?deposit or !dp <amt>** deposits your vpkt wallet balance into your bank.
    **?withdraw or !wd <amt>** brings back your deposited bank balance into your wallet.
    **?exch <siri wallet address>** converts your vpkt into mkpt Price: 500vsiri = 500siri
    **?vsiri** #explains what is bot coins.
    **?leaderboard or !lb <argument ex: 4>** Shows The top richest people with botcoins
    **?about** shows all information of the bot.
    **?help** Shows this command.
    **?bal** Shows Your Bot Coin Balance.
    **?claim** gives bot coins (u might get coins from 1-80).
    **?send <Member ping> <coins>** sends your bal to another person.
    **?pingnet** (Experimental) Pings each and every pools of siricoin and tells its stats.""", colour=discord.Colour.orange())
page2 = discord.Embed(title="Moderation Help Commands!:", description="""
    **?sysload** Shows the VPS CPU Stats.
    **?ping** Shows the latency of the bot.
    **?setclear <number> (Requires admin perms)** clears the messages that you mentioned.
    **?ban <mention mem> (Requires admin perms)** Bans the mentioned member in the guild.
    **?unban <member with discriminator> (Requires admin perms)** unbans the mentioned member in the guild.
    **?mute <mention mem> <Duration> (Requires admin perms)** mutes mentioned member for mentioned duration.
    **?unmute <member> (Requires admin perms)** unmutes mentioned member in the guild.
    **?kick <mention mem> (Requires admin perms)** kicks the mentioned member from the guild.""", colour=discord.Colour.orange())
page3 = discord.Embed(title="Shreyas-ITB Help Commands!:", description="""
    **This Commands IS ONLY ACCESSIBLE For Shreyas-ITB!**
    **?shutdown (Requires Shreyas)** If any emergency, This ShutsDown Mr.PKT.
    **?gstart <duration> <reward> (Requires Shreyas)** Hosts A giveaway and pics a winner.""", colour=discord.Colour.orange())

client.help_pages = [page1, page2, page3]

@client.command()
async def help(ctx):
    buttons = [u"\u23EA", u"\u2B05", u"\u27A1", u"\u23E9"] # skip to start, left, right, skip to end
    current = 0
    msg = await ctx.send(embed=client.help_pages[current])
    
    for button in buttons:
        await msg.add_reaction(button)
        
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)

        except asyncio.TimeoutError:
            return print("Timeout")

        else:
            previous_page = current
            if reaction.emoji == u"\u23EA":
                current = 0
                
            elif reaction.emoji == u"\u2B05":
                if current > 0:
                    current -= 1
                    
            elif reaction.emoji == u"\u27A1":
                if current < len(client.help_pages)-1:
                    current += 1

            elif reaction.emoji == u"\u23E9":
                current = len(client.help_pages)-1

            for button in buttons:
                await msg.remove_reaction(button, ctx.author)

            if current != previous_page:
                await msg.edit(embed=client.help_pages[current])

@client.command()
async def sysload(ctx):
    sysemb = discord.Embed(title="BOT Stats", description=f"""
CPU usage: ${await os_utils.cpu.usage()}%
RAM usage: ${math.round((os.totalmem() - os.freemem()) / 1000000)}MB
Server uptime: ${format(os.uptime())}""")
    sysemb.set_footer(f"Command Requested By {ctx.author.name}")
    await ctx.sent(embed=sysemb)

@client.command()
async def pingnet(ctx):
    await ctx.send("SiriCoin has no pools..")

@client.command()
@commands.cooldown(1, 86400, commands.BucketType.guild)
async def exch(ctx, walletid, amount=100):
    await ctx.send("Nothing happens for now! patience!")

# Main code ends :(
####################################################################
####################################################################

client.run("ODgyNjY2NDEwNzg5MTc1Mjk2.YS-tJw.6ydbhqvZFZoX_YG-3QZU0Is5dhU")
asyncio.run(client.db.close())
