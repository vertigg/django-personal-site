import asyncio
import datetime
import logging
import inspect
import json
import os
import random
import subprocess
import sys
import time
import gc
from datetime import datetime, timedelta

import discord

def __setup_django(root_path):
    import django

    os.chdir(root_path)

    # Django settings
    sys.path.append(root_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "VertigoProject.settings")

    django.setup()

#PROJECT_PATH = "/home/vertigo/homesite/django-epicvertigo"
PROJECT_PATH = r"C:\Users\EpicVertigo\Desktop\HomeSite"

__setup_django(PROJECT_PATH)


from discord.ext import commands
from discord.errors import InvalidArgument

from discordbot.models import DiscordLink, DiscordSettings, DiscordUser, Wisdom, Gachi, WFAlert
from discordbot.credentials import BOT_TOKEN, TEST_TOKEN
from discordbot.ext.utils import admin_command, mod_command, wisdom_info_formatter, get_random_entry
from discordbot.ext import utils, google_brawl, imgur_hb, warframe

logging.config.fileConfig('discordbot/logger.ini')
discordLogger = logging.getLogger('discordLogger')
botLogger = logging.getLogger('botLogger')

bot = commands.Bot(command_prefix='!',
                   description='Super duper halal bot for clowans. List of commands below')

@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name=DiscordSettings.objects.get(key='game').value))
    botLogger.info('Logged in as {0}:{1}'.format(bot.user.name, bot.user.id))


@bot.command(pass_context=True, hidden=True)
@admin_command
async def debug(ctx, *, code: str):
    """Evaluates code."""
    code = code.strip('` `')
    python = '```py\n{}\n```'
    try:
        result = eval(code)
        if inspect.isawaitable(result):
            result = await result
    except Exception as e:
        await bot.say(python.format(type(e).__name__ + ': ' + str(e)))
        result = None
        return
    await bot.say(python.format(result))

@bot.command(pass_context=True)
async def register(ctx):
    token = utils.generate_token(ctx.message.author.id)
    await bot.send_message(ctx.message.author, token)

@bot.command()
async def cytube():
    """Для тех кто не умеет добавлять сайты в закладки"""
    cytube_url = DiscordLink.objects.get(key='cytube')
    movies_url = DiscordLink.objects.get(key='movies')
    await bot.say('`Смотреть` <:bearrion:230370930600312832> {0}\n'
                  '`Брать кинцо` <:cruzhulk:230370931065749514> {1}'.format(cytube_url, movies_url))


@bot.command(hidden=True)
async def shles():
    """SHLES"""
    await bot.say(DiscordLink.objects.get(key='shles'))


@bot.command(pass_context=True)
async def avatar(ctx, mention=None):
    """Показывает аватарку юзера"""
    if mention == None:
        await bot.say(ctx.message.author.avatar_url)
        return
    if len(mention) is not 21 and len(mention) is not 22:
        await bot.say('`Как юзать - !avatar @User`')
        return
    if mention[2] == '!':
        mention = mention.replace('!', '')
    user = None
    for member in ctx.message.server.members:
        if member.id == mention[2:20]:
            user = member
    if user == None:
        await bot.say('`Нет такого юзера на сервере`')
    else:
        if user.avatar_url == '':
            await bot.say('`У юзера нет аватарки`')
        else:
            await bot.say(user.avatar_url)


@bot.command()
async def ip():
    """Напомните ип плс"""
    await bot.say(str(DiscordSettings.objects.get(key='ip')) + ' <:OSsloth:230773934197440522>')


@bot.group(pass_context=True)
async def mix(ctx):
    """Mixes !hb and !wisdom commands"""
    if not ctx.invoked_subcommand:
        wisdom_obj = get_random_entry(Wisdom)
        pic_url = utils.get_random_picture()
        if wisdom_obj is not None:
            await bot.say('{0}\n{1}'.format(wisdom_obj.text, pic_url))
                                        

@bot.command(pass_context=True, hidden=True)
async def low(ctx):
    if ctx.message.author.id == '127135903125733376':
        await bot.say(DiscordLink.objects.get(key='low'))
    else:
        await bot.say('<:bearrion:230370930600312832>')


@bot.group(pass_context=True)
async def ow(ctx):
    """Overwatch Rank"""
    if ctx.invoked_subcommand is None:
        query_set = (DiscordUser.objects
            .exclude(blizzard_id__exact='')
            .values_list('id', 'blizzard_id'))
        ow_players = {x[0] : x[1] for x in query_set}
        if ctx.message.content == '!ow':
            if ctx.message.author.id in ow_players:
                message = await utils.check_ow_rank(ctx.message.author.id, ow_players)
                await bot.say('`{0}, Current rank {1}`'.format(ctx.message.author.name, message))
            return
        else:
            content = ctx.message.content
            mention = content.split('!ow ')[1][2:20]
            if mention == '!22383766718644224':
                await bot.say('Я не играю в это говно <:ded:237151960359370753>')
                return
            if len(mention) is not 18 or not mention.isdigit():
                await bot.say('`How to use - !ow @User`')
                return
            if mention in ow_players:
                message = await utils.check_ow_rank(mention, ow_players)
                await bot.say('`{0}, Current rank {1}`'.format(ow_players[mention].split('-')[0], message))
            else:
                await bot.say("Can't find player in database")


@ow.command(pass_context=True)
async def ladder():
    global ow_lock, ow_timeout
    if not ow_lock and time.time() - ow_timeout >= 300:
        try:
            ow_lock = True
            ow_players = (DiscordUser.objects.exclude(blizzard_id__exact='').values_list('blizzard_id', flat=True))
            tmp_message = await bot.say('`Loading ladder`')
            futures = []
            ladder = {}
            for k in ow_players:
                futures.append(utils.check_ow_ladder(k, ow_players, ladder))
            await bot.loop.create_task(asyncio.wait(futures))
            sorted_ladder = sorted(ladder.items(), key=lambda x: x[1], reverse=True)
            messageText = ''
            for x in sorted_ladder:
                messageText += '    {0} - {1}\n'.format(x[1], x[0])
            await bot.edit_message(tmp_message, '<:OSsloth:230773934197440522> \n```xl\nOverwatch rankings\n\n{0}```'.format(messageText))
            ow_timeout = round(time.time())
            await asyncio.sleep(300)
            ow_lock = False
        except Exception as e:
            botLogger.error(e)
            ow_lock = False
    else:
        cooldown = 300 - round((time.time() - ow_timeout))
        await bot.say("Next update will be available in {} seconds".format(cooldown))


@bot.group(pass_context=True)
async def gachi(ctx):
    """Take it boy"""
    if not ctx.invoked_subcommand:
        gachi_obj = get_random_entry(Gachi)
        if gachi_obj is not None:
            await bot.say(gachi_obj.url)


@gachi.command(pass_context=True)
@mod_command
async def add(ctx, url: str):
    # Add regex for links
    Gachi.objects.create(url=url)
    await bot.say('{} added'.format(url))


@bot.command(hidden=True)
async def firstrule():
    await bot.say('Never hook first <:smart:282452131552690176>')


@bot.command(hidden=True)
async def secondrule():
    await bot.say("You can't counter Pharah <:Kappa:230228691945390080>")


@bot.command(hidden=True)
async def thirdrule():
    await bot.say("Ко мне говно <:4Head:230227653783846912>")


@bot.group(pass_context=True)
async def wiki(ctx):
    """Википедия в Дискорде, не отходя от кассы"""
    article = str(ctx.message.content).replace('!wiki ', '')
    if not ctx.invoked_subcommand:
        if article == '!wiki':
            await bot.say('`Пример использования "!wiki Дупель"`')
        else:
            try:
                await bot.say('`{}`'.format(utils.wiki(article)[0]))
            except Exception as e:
                botLogger.error(e)
                await bot.say(str(e))


@wiki.command()
async def lang(string: str):
    """Сменить язык Вики (Доступные языки - en, ru, uk, el)"""
    await bot.say(utils.wikibotlang(string))


@wiki.command(pass_context=True)
async def link(ctx):
    """Выдать ссылку на статью (если она существует)"""
    wikireq = str(ctx.message.content).replace('!wiki link ', '')
    await bot.say(utils.wiki(wikireq)[1])


@bot.group(pass_context=True)
async def hb(ctx):
    """Нет слов"""
    if not ctx.invoked_subcommand:
        await bot.say(utils.get_random_picture())


@hb.command()
async def update():
    """Обновить список картинок из альбома ХБ"""
    await bot.say(imgur_hb.update())


@bot.group(pass_context=True)
async def wisdom(ctx):
    """Спиздануть мудрость клоунов"""
    if not ctx.invoked_subcommand:
        wisdom_obj = get_random_entry(Wisdom)
        if wisdom_obj is not None:
            await bot.say(wisdom_obj.text)


@wisdom.command(pass_context=True)
@mod_command
async def add(ctx, *, text:str):
    """Добавить новую мудрость клоунов"""
    wisdom_text = text.strip()
    Wisdom.objects.create(
        text = wisdom_text,
        date = datetime.now(),
        author_id = ctx.message.author.id
    )
    await bot.say('{} added'.format(wisdom_text))


@wisdom.command(pass_context=True, hidden=True)
@admin_command
async def remove(ctx, wisdom_id:int):
    """Removes wisdom by given id in ctx"""
    if isinstance(wisdom_id, int):
        entry = Wisdom.objects.filter(id=wisdom_id).delete()
        if entry[0] is not 0:
            await bot.say('Wisdom {} removed'.format(wisdom_id))


@wisdom.command(hidden=True, pass_context=True)
@mod_command
async def info(ctx):
    """Show 5 last wisdoms with id and author's name and some info"""
    last_update_time = DiscordSettings.objects.get(key='cache_update').value
    if datetime.now() - datetime.strptime(last_update_time, '%Y-%m-%d %H:%M:%S.%f') > timedelta(days=1):
        utils.update_display_names(bot.servers)
        utils.refresh_wisdom_history()
    cached_nicknames = utils.get_nickname_cache()
    await bot.say(await wisdom_info_formatter(cached_nicknames))


@wisdom.command(hidden=True, pass_context=True)
@admin_command
async def refresh(ctx):
    utils.update_display_names(bot.servers)
    message = utils.refresh_wisdom_history()
    await bot.say(message)


@bot.group(pass_context=True)
async def brawl(ctx):
    """Kill me pls"""
    if not ctx.invoked_subcommand:
        await bot.say(google_brawl.randomize_phrase(brawl_list))


@brawl.command()
async def update():
    global brawl_list
    """Обновить текущий словарь"""
    brawl_list = google_brawl.check_for_updates()
    if brawl_list:
        await bot.say('`Brawl table has been successfully updated`')
    else:
        await bot.say("`Something wrong with brawl lists. Please check logs for more info`")


@brawl.command()
async def info():
    """Ссылка на файл со словарем"""
    await bot.say(DiscordLink.objects.get(key='brawl_sheet'))


@bot.command()
async def roll():  # Roll int() from 1 to 100
    """Ролит число от 1 до 100"""
    rollresult = random.randint(1, 100)
    await bot.say(rollresult)


@bot.command()
async def friday():
    """Время в задницу"""
    await bot.say(DiscordLink.objects.get(key='friday'))


@bot.command()
async def choose(*choices: str):
    """Выбор между стульями"""
    await bot.say(random.choice(choices))


@bot.command()
async def free():
    """Святые писания"""
    await bot.say('`Живи молодым и умри молодым` {}'.format(DiscordLink.objects.get(key='free')))


@bot.group(pass_context=True)
async def kf(ctx):
    """Ссылка на файл статистики по КФ2"""
    if not ctx.invoked_subcommand:
        await bot.say(DiscordLink.objects.get(key='kf2'))


@kf.command()
async def update():  # Update kf2 gdrive file
    """Обновить файл статистики по КФ2"""
    global extScriptLock
    if extScriptLock == True:
        await bot.say("`Скрипт еще работает, не задрачивай меня`")
    if extScriptLock == False:
        # extScriptLock = await SteamStats.BotUpdate({"GAMEID":"252950","WSNAME":"Rocket League",'GSNAME':'Steam Achievements', 'fix_icons':False, 'firstTime':False, 'decorate':False, 'nodesc':False})
        p = subprocess.Popen(["python3", "discordbot/SteamStats.py",
                              "-g", "232090",
                              "-ws", "KF2"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        #botLogger.info(p.communicate()) # for debug
        await bot.say("`Скрипт запущен, помолимся.`")
        botLogger.info('[KFGOOGLE]: Script started')
        extScriptLock = True
        sleeptime = 5
        while p.poll() == None:
            await asyncio.sleep(sleeptime)
        else:
            await bot.say("`Таблицы ачивок обновлены`")
            extScriptLock = False
            botLogger.info('[KFGOOGLE]: Script finished')


@bot.command(pass_context=True)
@mod_command
async def game(ctx, *args):  # Change game in status
    """Сменить боту игру"""
    game = ' '.join(args)
    if not game:
        await bot.say('`How to use: "!game Game Name"`')
    else:
        DiscordSettings.objects.filter(key='game').update(value=game)
        await bot.change_presence(game=discord.Game(name=game))
        await bot.say('Status changed', delete_after=15)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

async def warframe_alert_watchdog():
    await bot.wait_until_ready()
    server = bot.get_server(id='178976406288465920')
    while not bot.is_closed:
        new_alerts = WFAlert.objects.filter(announced=False)
        for alert in new_alerts:
            try:
                matches = []
                if alert.keywords:
                    keywords = alert.keywords.split(',')

                    for key in keywords:
                        if key in warframe.RESOURCES:
                            matches.append(warframe.RESOURCES[key])
                
                if matches:
                    if len(matches) is 2:
                        q1 = DiscordUser.objects.select_related().filter(**{'wf_settings__{}'.format(matches[0]):True})
                        q2 = DiscordUser.objects.select_related().filter(**{'wf_settings__{}'.format(matches[1]):True})
                        subscribers = q1.union(q2)
                    else:
                        query_filter = {'wf_settings__{}'.format(matches[0]) : True}
                        subscribers = DiscordUser.objects.select_related().filter(**query_filter)  
                    
                    for sub in subscribers:
                        try:
                            user = server.get_member(sub.id)
                            await bot.send_message(user, '```{}```'.format(alert.content))
                        except InvalidArgument:
                            pass
            except Exception as e:
                logging.error(e)
                pass
            alert.announced=True
            alert.save()
        await asyncio.sleep(60)


if __name__ == '__main__':
    botLogger.info('Script started')
    brawl_list = google_brawl.check_for_updates()
    imgur_hb.update()
    extScriptLock = False
    ow_lock = False
    ow_timeout = 0

    bot.loop.create_task(warframe_alert_watchdog())
    bot.run(BOT_TOKEN)
