import os
import sys
import json
from wit import Wit
from twitchio.ext import commands

bot = commands.Bot(
    # set up the bot
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[os.environ['CHANNEL']]
)
enabledCommands = {
    'test':'test Response',
    'toxicity': 'AutoMod has detected toxicity from ',
    'toxicity_racism': 'Message logged for review, AutoMod has detected racism from ',
    'toxicity_sexism': 'Automod has detected sexism from ',
    'toxicity_harassment': 'Automod has detected harassment from ',
    'ban_message': '/timeout ',
    'ban_time': '500',
    'plan_request': 'No Current Plan',
    'streamer_request': ' This is Jacy, He currently plays Valorant and lives in Canada',
    'song_request': 'Thanks for the song request!',
    'song_get': 'The current song is Unknown',
    'settings': 'Current DPI is 650, Valorant sens: 0.36, all low graphics settings'
}

song_requests = []

#initialize Wit
wit_token=os.environ['WIT_TOKEN']
witClient = Wit(access_token = wit_token)
#test = witClient.message('what is this song?')
#print('response' + str(test))

def handleEntity(entities):
    retEnts = []
    if entities:
        for entity,info in entities.items():
            if info[0]['confidence'] > 0.8:
                retEnts.append(str(entity))
    return retEnts

def moderate(res, authors):
    retResp = []
    intent = str(res['intents'][0]['name'])
    confidence = res['intents'][0]['confidence']
    ent = res['entities']
    if 'toxicity' in intent and confidence >= 0.8:
        if 'racism' in intent:
            entTrait = handleEntity(ent)
            #for extreme racism, permaban
            if 'racism:racism' in entTrait:
                resp = enabledCommands[intent] + f'@{authors}'
                retResp.append(resp)
                resp = '/ban' + f'{authors}'
                retResp.append(resp)
            #if message is actually positive we skip it and don't moderate
            elif 'positivity:positivity' not in entTrait:
                resp = enabledCommands[intent] + f'@{authors}'
                retResp.append(resp)
                resp = enabledCommands['ban_message'] + f'{authors}' + enabledCommands['ban_time']
                retResp.append(resp)
        
        #handle sexism
        elif 'sexism' in intent:
            resp = enabledCommands[intent] + f'@{authors}'
            retResp.append(resp)
        
        #handle harassment
        elif 'harassment' in intent:
            resp = enabledCommands[intent] + f'@{authors}, AutoMod reminds you to keep chat clean'
            retResp.append(resp)
        
        #other non moderated answers for FAQ's handled here
        else:
            resp = enabledCommands[intent] + f'@{authors}'
            retResp.append(resp)
    
    #handle song requests
    elif 'song_request' == intent:
        requested = handleEntity(ent)
        song_requests.append(requested)
        resp = enabledCommands[intent]
        retResp.append(resp)
    
    else:
        resp = enabledCommands[intent]
        retResp.append(resp)
    
    return retResp

#update a FAQ answer or parts of the moderation messages
def updateFunc(content):
    splitCommand = content.split(maxsplit=2)
    if splitCommand[0] == '!update' and splitCommand[1] in enabledCommands:
        currentMsg = enabledCommands[splitCommand[1]]
        enabledCommands[splitCommand[1]] = splitCommand[2]
        msg = 'Updated Autoreply for '+ splitCommand[1] + ' from ' + currentMsg + ' to ' + splitCommand[2]
        return msg
    else:
        return 'Incorrect format: use \'!update <command to update> <new message>\''

#request list clearing and printing
def reqListFunc(content):
    splitCommand = content.split(maxsplit=2)
    if splitCommand[0] == '!reqList' and splitCommand[1] == 'clear':
        song_requests.clear()
        return 'Request List Cleared'
    elif splitCommand[0] == '!reqList' and splitCommand[1] == 'show':
        return str(song_requests)
    else:
        return 'Incorrect format: use \'!reqList <clear|show>\''


@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f"{bot.nick} is online!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    await ws.send_privmsg(os.environ['CHANNEL'], f"/me has landed!")

@bot.event
async def event_message(ctx):
    
    #ignore itself
    if ctx.author.name.lower() == bot.nick.lower() or ctx.author.name.lower() == 'nightbot':
        return
    
    #handle hardcoded commands prefixed with !
    await bot.handle_commands(ctx)
    
    #send wit api message and respond with json predictions if not a command message
    if ctx.content[0] != '!':
        res = witClient.message(ctx.content)
        print(res)
        if len(res['intents']) > 0:
            results = moderate(res,ctx.author.name)
            for message in results:
                await ctx.channel.send(message)
            #await ctx.channel.send('response: ' + str(res['intents'][0]['name']) + '\n confidence: ' + str(res['intents'][0]['confidence']))
        
        #await ctx.channel.send(str(res))

@bot.command(name='update')
async def update(ctx):
    msg = updateFunc(ctx.content)
    await ctx.send(msg)

@bot.command(name='reqList')
async def reqList(ctx):
    msg = reqListFunc(ctx.content)
    await ctx.send(msg)

def systemTest():
    print('Input stopTest to end test environment and close program')
    while True:
        testMsg = input()
        if testMsg == 'stopTest':
            break
        if testMsg[0] == '!':
            if 'update' in testMsg:
                msg = updateFunc(testMsg)
            elif 'reqList' in testMsg:
                msg = reqListFunc(testMsg)
            print(msg)
            continue
        
        res = witClient.message(testMsg)
        #print(res)
        if len(res['intents']) > 0:
            results = moderate(res,'TestUser')
            for message in results:
                print (message)


if __name__ == "__main__":
    if len(sys.argv) > 0 and sys.argv[1] == 'test':
        systemTest()
    elif len(sys.argv) > 0 and sys.argv[1] == 'run':
        bot.run()
    else:
        print('Usage: pipenv run python autoBot.py <test|run>')

#TODO:
#record video
#finish submission