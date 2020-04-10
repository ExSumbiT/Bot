import requests, re, discord
from discord.ext import commands
from bs4 import BeautifulSoup
from langdetect import detect
TOKEN = 'NjkxNjkwNjI3MjU5NDMyOTgx.XnjpXg.3j1SyoRnS_8BX5dkJ7pRiOntlEg'
log_url = 'https://forum.excalibur-craft.ru/login/'
url = 'https://forum.excalibur-craft.ru/topic/125632-equilibrium/'
url_edit = 'https://forum.excalibur-craft.ru/topic/125214-for-mkzet/'
bot = commands.Bot(command_prefix='|')


@bot.command()
async def up(ctx):
    activity = discord.Activity(name="SumbiT'a", type=discord.ActivityType.listening)
    await bot.change_presence(activity=activity)


def add(math):
    data = int(math[0].split('+')[0]) + int(math[0].split('+')[1])
    return {'answer': str(data)}


def login(session):
    req = session.get(log_url)
    math = re.findall('Вопрос: (.*?) =', req.text)
    req_f = session.post(log_url, add(math))
    csrf = re.findall('name="csrfKey".*?value="(.*?)"', req_f.text)
    text = session.get(
        f'''https://forum.excalibur-craft.ru/login/?csrfKey={csrf[0]}&auth=exlord&password=Kola_2102_&remember_me=1&_
        processLogin=usernamepassword&_processLogin=usernamepassword''')
    return text


def parse_post(text, find_nick, comment_url=None):
    posts = text.find_all('article', {'class': ['cPost', 'ipsComment']})
    post = []
    for _ in posts:
        nick_bd_write = open('nicks.txt', 'a')
        nick_bd_read = open('nicks.txt', 'r')
        nick_list = nick_bd_read.read().split('\n')
        nick = str(_.find('div', {'class': 'cAuthorPane'}).find('a').text)
        if nick in nick_list:
            if nick == str(find_nick):
                post.append(str(_.find('div', {'data-role': 'commentContent'}).text).replace('\t', '').replace('\n\n\n', '\n'))
                if comment_url is not None:
                    comment_url.append(str(_.find('a', {'data-action': 'editComment'}).get('href')))
                return post
            continue
        else:
            nick_bd_write.write(nick+'\n')
            nick_bd_write.close()
            post.append(str(_.find('div', {'data-role': 'commentContent'}).text).replace('\t', '').replace('\n\n\n', '\n'))
    return post


def get_post(nick):
    s = requests.session()
    login(s)
    posts = []
    page = s.get(url)
    rel = True
    while 1:
        if rel:
            soup = BeautifulSoup(page.text, 'html.parser')
            posts += parse_post(soup, nick)
            rel = bool(soup.find('link', {'rel': 'next'}))
            try:
                page = s.get(soup.find('link', {'rel': 'next'}).get('href'))
            except AttributeError:
                pass
        else:
            soup = BeautifulSoup(page.text, 'html.parser')
            posts += parse_post(soup, nick)
            break
    return posts


def edit_post(nick):
    s = requests.session()
    auth = login(s)
    csrf = re.findall('csrfKey.*?"(.*?)"', auth.text)
    soup = BeautifulSoup(s.get(f'''https://forum.excalibur-craft.ru/topic/125214-for-mkzet/''').text, 'html.parser')
    plupload = soup.find('input', {'name': 'plupload'}).get('value')
    MAX_FILE_SIZE = soup.find('input', {'name': 'MAX_FILE_SIZE'}).get('value')
    edit_url = []
    post = parse_post(soup, nick, edit_url)
    ppost = post[0].replace(' ', ' ').split('\n')

    ppost = [x for x in ppost if (x and len(x) > 2)]
    for _ in range(len(ppost)):
        if 'сказал' in ppost[_] or 'Изменено' in ppost[_]:
            del ppost[_]
    if detect(ppost[0]) == 'ru':
        del ppost[0]

    pg = s.get(f'''{''.join(edit_url)}''',
               params={
                       'form_submitted': '1',
                       'csrfKey': csrf[2],
                       'MAX_FILE_SIZE': MAX_FILE_SIZE,
                       'plupload': plupload,
    'comment_value': f'''[font=CONSOLAS][left]{ppost[0]}[left]
[left]{ppost[1]}[/left]
[left]{ppost[2]}[/left]
[left]{ppost[3]}[/left]
[left]{ppost[4]}[/left]
[left]{ppost[5]}[/left]
[left]{ppost[6]}[/left]
[left]{ppost[7]}[/left]
[left]{ppost[8]}[/left]
[left]{ppost[9]}[/left][/font]
[center][img]https://i.ibb.co/wLWh9Xk/accept.png[/img][/center]'''})


@bot.command()
async def clear(ctx, amount=100):
    channel = ctx.message.channel
    messages = []
    async for message in channel.history(limit=amount):
        messages.append(message)
    await channel.delete_messages(messages)


@bot.command()
async def get(ctx, nick=''):
    await clear(ctx, amount=1)
    if len(nick) >= 3:
        await ctx.send(get_post(nick)[0])
    else:
        for post in get_post(nick):
            msg = await ctx.send(post)#'@everyone'+
            await msg.add_reaction('❌')
            await msg.add_reaction('✅')


#@bot.command()
#async def edit(ctx, nick):
    # try:
    #     edit_post(nick)
    #     await ctx.send('all ok!')
    # except requests.exceptions.MissingSchema:
    #     await ctx.send(f'"{nick}" not found')


@bot.command()
async def stat(ctx):
    pass


bot.run(TOKEN)