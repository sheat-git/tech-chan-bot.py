import os
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

TOKEN = os.environ['DISCORD_BOT_TOKEN']

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
slash = SlashCommand(bot)

bot_id = 906230768865538079
teamRoleIds = {654258617188483073:'コンサート', 654259540732280877:'コンテスト', 654258761208430612:'野外ステージ', 906388096998850570:'テスト'}

@slash.slash(
    name='attend',
    description='出欠確認',
    options=[
        create_option(
            name='title',
            description='確認表のタイトル',
            option_type=3,
            required=True
        )
    ])
async def _attend(ctx: SlashContext, *, arg):
    text = \
        f'__**{arg}**の出欠確認__\n' +\
        '出席 :o:\n' +\
        '欠席 :x:'
    message = await ctx.send(content=text)
    await message.add_reaction('⭕')
    await message.add_reaction('❌')

@bot.command()
async def attend(ctx, *, arg):
    text = \
        f'__**{arg}**の出欠確認__\n' +\
        '出席 :o:\n' +\
        '欠席 :x:'
    message = await ctx.send(content=text)
    await message.add_reaction('⭕')
    await message.add_reaction('❌')

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot_id:
        return
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    Ousers = None
    Xusers = None
    for reaction in message.reactions:
        if reaction.emoji == '⭕':
            Ousers = await reaction.users().flatten()
        elif reaction.emoji == '❌':
            Xusers = await reaction.users().flatten()
    await message.edit(content=makeContent(message, Ousers, Xusers))

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.user_id == bot_id:
        return
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    Ousers = None
    Xusers = None
    for reaction in message.reactions:
        if reaction.emoji == '⭕':
            Ousers = await reaction.users().flatten()
        elif reaction.emoji == '❌':
            Xusers = await reaction.users().flatten()
    await message.edit(content=makeContent(message, Ousers, Xusers))


def makeContent(message, Ousers, Xusers):

    guild = message.guild

    class person:
        def __init__(self):
            self.name = None
            self.team = None
            self.gen = None
        
    def haveUsers(users):
        if users is None:
            return False
        if not users:
            return False
        if len(users) >= 2:
            return True
        if users[0].id == bot_id:
            return False
        else:
            return True

    def toPersonList(users):
        pList = []
        for user in users:
            if user.id == bot_id:
                continue
            member = guild.get_member(user.id)
            p = person()
            p.name = member.nick
            if p.name is None:
                p.name = member.name
            for role in member.roles:
                p.team = teamRoleIds.get(role.id, p.team)
                if role.name.isdigit():
                    p.gen = int(role.name[-2:])
            pList.append(p)
        return pList
    
    def toTeamLists(pList):
        teamLists = {'コンサート':[], 'コンテスト':[], '野外ステージ':[], 'テスト':[]}
        for p in pList:
            teamLists[p.team].append(p)
        return teamLists
    
    def groupByGen(teamList):
        genLists = {}
        for p in teamList:
            if not p.gen in genLists:
                genLists[p.gen] = [p]
            else:
                genLists[p.gen].append(p)
        return sorted(genLists.items(), key=lambda x:x[0])
    
    def toText(users):
        text = ''
        pL = toPersonList(users)
        tLs = toTeamLists(pL)
        for teamName, teamList in tLs.items():
            if not teamList:
                continue
            if not text:
                text = '```'
            else:
                text += '\n'
            text += teamName + '\n'
            genLists = groupByGen(teamList)
            for gen, pList in genLists:
                text += f'{gen}  {pList[0].name}\n'
                if len(pList) == 1:
                    continue
                for p in pList:
                    text += f'    {p.name}\n'
        return text[:-1] + '```'
    
    text = message.content.split('\n')[0]
    text += '\n出席 :o:'
    if haveUsers(Ousers):
        text += toText(Ousers)
    text += '\n欠席 :x:'
    if haveUsers(Xusers):
        text += toText(Xusers)
    return text


bot.run(TOKEN)
