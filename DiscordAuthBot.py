import re, discord
from discord.ext import commands, tasks
import asyncio
import random
import sqlite3
from tabulate import tabulate
from datetime import datetime


conn = sqlite3.connect()  # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()


bot = commands.Bot(command_prefix='|')


@bot.event
async def on_ready():
    birthday_notification.start()
    activity = discord.Activity(name="мультики", type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def prg(ctx, amount=500):
    await ctx.channel.purge(limit=amount + 1)


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def sendto(ctx, channel_id: int, everyone: int, *, content):
    await ctx.channel.purge(limit=1)
    if bool(everyone):
        await bot.get_channel(channel_id).send("@everyone\n" + content)
    else:
        await bot.get_channel(channel_id).send(content)


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def send(ctx, *, content):
    await ctx.channel.purge(limit=1)
    await ctx.channel.send(content)


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def edit(ctx):
    table = []
    main_table = await bot.get_channel(660799528856715300).fetch_message(739440611731439697)
    # main_table------------------------------------------------------------------------
    for row in cursor.execute(f"SELECT nickname,real_name, strftime('%d-%m-%Y', date(birthday/1000, 'unixepoch')), "
                              f"(strftime('%Y','now')-strftime('%Y',date(birthday/1000,'unixepoch')))-"
                              f"(strftime('%m-%d','now')<strftime('%m-%d',date(birthday/1000,'unixepoch'))), "
                              f"country, vacation FROM members where vacation='Нет' ORDER BY member_id"):
        table.append([row[0], row[1], row[2], row[3], row[4], row[5]])
    await main_table.edit(content='@everyone\n' + '```css\n' + tabulate(table,
                                                                        headers=['NICKNAME', 'NAME', 'BIRTHDAY', 'AGE',
                                                                                 'COUNTRY', 'VACATION'],
                                                                        tablefmt="simple",
                                                                        showindex=[x + 1 for x in
                                                                                   range(len(table))]) + '```')
    # vac_table--------------------------------------------------------------------------
    len_main_table = len(table)
    table.clear()
    vac_table = await bot.get_channel(660799528856715300).fetch_message(739440690391679017)
    for row in cursor.execute(f"SELECT nickname,real_name, strftime('%d-%m-%Y', date(birthday/1000, 'unixepoch')), "
                              f"(strftime('%Y','now')-strftime('%Y',date(birthday/1000,'unixepoch')))-"
                              f"(strftime('%m-%d','now')<strftime('%m-%d',date(birthday/1000,'unixepoch'))), "
                              f"country, vacation FROM members where vacation!='Нет' ORDER BY member_id"):
        table.append([row[0], row[1], row[2], row[3], row[4], row[5]])
    await vac_table.edit(content='```css\n' + tabulate(table,
                                                       headers=['NICKNAME', 'NAME', 'BIRTHDAY', 'AGE',
                                                                'COUNTRY', 'VACATION'],
                                                       tablefmt="simple",
                                                       showindex=[x + len_main_table + 1 for x in
                                                                  range(len(table))]) + '```' + '\n@everyone')


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def addm(ctx, user: discord.Member, role: str):
    await ctx.channel.purge(limit=1)
    await user.remove_roles(discord.utils.get(ctx.message.guild.roles, name='◈═══════◈Гость◈═══════◈'))
    await user.add_roles(discord.utils.get(ctx.message.guild.roles, name='●────────●Клан●────────●'))
    await user.add_roles(discord.utils.get(ctx.message.guild.roles, name='▬▬▬▬▬●Equilibrium●▬▬▬▬▬'))
    await user.add_roles(discord.utils.get(ctx.message.guild.roles, id=727298785654472776))
    await user.add_roles(discord.utils.get(ctx.message.guild.roles, id=727299629372145684))
    await user.add_roles(discord.utils.find(lambda r: role in r.name, ctx.message.guild.roles))
    # news
    await bot.get_channel(660797576362328066).send(f"@everyone\nПриветствуем нового участника клана - <@{user.id}>")
    emb = discord.Embed(colour=discord.Color.dark_blue())
    emb.add_field(name="Здравствуй!", value="1. Подай заявку на вступление в клан\n"
                                            "https://excalibur-craft.ru/index.php?do=clans&go=profile&id=3717\n"
                                            "2. Вступи в сообщество клана на форуме\n"
                                            "https://forum.excalibur-craft.ru/clubs/68-equilibrium/")
    emb.set_footer(text="Добро пожаловать!")
    # clan-chat
    await bot.get_channel(660800271965880331).send(f"<@{user.id}>", embed=emb)
    try:
        add_user_to_db(user)
    except:
        await bot.get_channel(660808504646303744).send(
            f"Что-то пошло не так, вызывайте экзорциста <@{456951428397924352}>!")
    await edit(ctx)


@bot.command(pass_context=True)
async def ping(ctx):
    await ctx.send(f'{ctx.author.mention}, ДА РАБОТАЮ Я, ОТВАЛИ!')


@bot.event
async def on_message(message):
    guild = message.guild
    if message.channel.name == "📩доступ":
        emj = bot.get_emoji(id=662134292058734614)

        def check(reaction, user):
            adm = [456951428397924352, 247029882519945218, 269165112516935680, 517349425371414538]
            return any(us == user.id for us in adm) and reaction.emoji == emj

        async def add_role(content):
            if ' ' in content:
                content = content.replace(' ', '')
            msg = content.split("\n")
            await message.author.edit(nick=f'{msg[0].split(".")[1]} [{msg[2].split(".")[1]}]')
            await message.author.remove_roles(discord.utils.get(bot.guilds[0].roles, id=662080379330494474))
            await message.author.add_roles(discord.utils.get(bot.guilds[0].roles, id=660617694118150184))
            await message.author.add_roles(discord.utils.get(bot.guilds[0].roles, id=660598561536475146))
            await message.author.add_roles(discord.utils.get(bot.guilds[0].roles, id=675800637904257040))
            clans = ['▬▬▬▬▬▬●Quasar●▬▬▬▬▬▬', '▬▬▬▬▬▬●BestLife●▬▬▬▬▬▬', '▬▬▬▬▬●AVALON●▬▬▬▬▬',
                     '▬▬▬▬▬▬●Pride●▬▬▬▬▬▬', '▬▬▬▬▬▬●PrimalZ●▬▬▬▬▬▬', '▬▬▬▬▬▬●Mortes●▬▬▬▬▬▬',
                     '▬▬▬▬▬▬●Ordo●▬▬▬▬▬▬', '▬▬▬▬▬●DarkElite●▬▬▬▬▬', '▬▬▬▬▬▬●Rise●▬▬▬▬▬▬',
                     '▬▬▬▬▬▬●Revolt●▬▬▬▬▬▬', '▬▬▬▬▬●LostParadise●▬▬▬▬▬']
            clan = ''.join([c for c in clans if msg[1].split(".")[1] in c])
            if clan:
                await message.author.add_roles(discord.utils.get(bot.guilds[0].roles, id=683415819409293386))
                await message.author.add_roles(
                    discord.utils.get(bot.guilds[0].roles, name='●────────●Клан●────────●'))
                await message.author.add_roles(discord.utils.get(bot.guilds[0].roles, name=clan))

        try:
            reaction, user = await bot.wait_for('reaction_add', check=check)
        except asyncio.TimeoutError:
            await message.channel.send('👎')
        else:
            # users = await reaction.users().flatten()
            if "\n" in message.content:
                await add_role(message.content)
            else:
                channel = message.channel
                messages = []
                async for msg in channel.history(limit=3):
                    messages.append(msg.content)
                messages.reverse()
                ms = ''
                for m in messages:
                    ms += m + '\n'
                await add_role(ms)
    elif message.channel.id == 727293535727911566:
        try:
            color_role = discord.utils.get(guild.roles, name='●────────●Цвет●────────●')
            perms_role = discord.utils.get(guild.roles, name='●────────●Права●────────●')
            user = message.author
            content = message.content
            if ' ' in content:
                content = content.replace(' ', '')
            color_name = content.split("\n")[1].split(".")[1]
            role_create = False
            for r in guild.roles:
                if r.name.lower() in color_name.lower():
                    new_role = r
                    role_create = True
            if not role_create:
                new_role = await guild.create_role(name=color_name,
                                                   colour=discord.Colour(int(color_name.replace('#', '0x'), 16)))
                await new_role.edit(position=random.randint(perms_role.position + 1, color_role.position - 1))
            if color_role in user.roles:
                for _ in range(len(user.roles)):
                    if user.roles[_].name == color_role.name:
                        if user.roles[_ - 1].name == perms_role.name:
                            pass
                        await user.remove_roles(user.roles[_ - 1])
                        await user.add_roles(new_role)
                        break
                await message.add_reaction(bot.get_emoji(id=662134292058734614))
            else:
                await user.add_roles(color_role)
                await user.add_roles(new_role)
                await message.add_reaction(bot.get_emoji(id=662134292058734614))
        except:
            await message.add_reaction(bot.get_emoji(id=662134317446725633))
    else:
        pass
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)
    if payload.channel_id == 660665545800024083:
        role = discord.utils.get(guild.roles, id=675800637904257040)
        role_to_remove = discord.utils.get(guild.roles, name="Ожидающий")
        if role in user.roles:
            await user.remove_roles(role_to_remove)
    else:
        pass


def add_user_to_db(user):
    nickname = re.search(r'[^\W*]\w+', user.display_name)[0]
    real_name = re.search(r'(?<=\[).+?(?=\])', user.display_name)[0]
    cursor.execute(f"SELECT nickname FROM members where nickname='{nickname}'")
    if cursor.fetchone() is None:
        cursor.execute(
            f"INSERT INTO members(nickname, real_name, member_id) select ?,?,max(member_id)+1 from members",
            (nickname, real_name,))
    else:
        pass
    conn.commit()


@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
@bot.command(pass_context=True)
async def change(ctx, nickname: str, *, args: str):
    arg = args.split('=')
    if arg[0] == 'id':
        cursor.execute(f"update members set member_id=member_id+1 where member_id>={int(arg[1])} and "
                       f"member_id<(select member_id from members where nickname=?)", (nickname,))
        cursor.execute(f"update members set member_id={int(arg[1])} where nickname=?", (nickname,))
    elif arg[0] == 'birthday':
        cursor.execute(f"UPDATE members SET {''.join(arg[0])}=(strftime('%s', {arg[1]})*1000) "
                       f"where nickname=?", (nickname,))
    else:
        cursor.execute(f"UPDATE members SET {''.join(arg[0])}={arg[1]} where nickname=?", (nickname,))
    conn.commit()
    await edit(ctx)


@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
@bot.command(pass_context=True)
async def cmd(ctx, *, command: str):
    cursor.execute(f"{''.join(command)}")
    conn.commit()


@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
@bot.command(pass_context=True)
async def remove(ctx, nickname: str):
    cursor.execute(f"update members set member_id=member_id-1 where member_id>(select member_id from members "
                   f"where nickname=?)", (nickname,))
    cursor.execute(f"delete from members where nickname=?", (nickname,))
    conn.commit()
    await edit(ctx)


@tasks.loop(hours=24)
async def birthday_notification(ctx):
    channel = bot.get_channel(660808504646303744)
    emoji = bot.get_emoji(733391075208593479)
    message = f' сегодня День Рождения{emoji}\nОт всего нашего мини сообщества, поздравляем тебя с этим днем!'
    bday = []
    for row in cursor.execute(f"select strftime('%d-%m', date(birthday/1000, 'unixepoch')) from members"):
        bday.append(row[0])
    bday.append('02-08')
    today = datetime.strftime(datetime.now(), '%d-%m')
    if today in bday:
        for row in cursor.execute(f"select nickname from members "
                                  f"where (strftime('%d-%m', date(birthday/1000, 'unixepoch')))=?", (today,)):
            user = discord.utils.find(lambda u: row[0] in u.display_name, channel.guild.members)
            await channel.send('@everyone, у ' + user.mention + message)
    else:
        pass


@birthday_notification.before_loop
async def before():
    f = '%H:%M'
    now = datetime.strftime(datetime.now(), f)
    diff = (datetime.strptime('09:00', f) - datetime.strptime(now, f)).total_seconds()
    if diff < 0:
        diff += 86400
    await asyncio.sleep(diff)


bot.run()
