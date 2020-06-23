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
    'ban_message': '/timeout ',
    'ban_time': '500',
    'plan_request': 'No Current Plan',
    'streamer_request': ' This is Jacy, He currently plays Valorant and lives in Canada',
    'song_request': 'Thanks for the song request!',
    'song_get': 'The current song is Unknown',
}

song_requests = []
suspected_racism = []

wit_token=os.environ['WIT_TOKEN']

witClient = Wit(access_token = wit_token)
#test = witClient.message('what is this song?')
#print('response' + str(test))

def moderate(res, authors):
    retResp = []
    intent = str(res['intents'][0]['name'])
    confidence = res['intents'][0]['confidence']
    if 'toxicity' in intent and confidence >= 0.8:
        if 'racism' in intent:
            resp = enabledCommands[intent] + f'@{authors}'
            retResp.append(resp)
            resp = enabledCommands['ban_message'] + f'{authors}' + enabledCommands['ban_time']
            retResp.append(resp)
        else:
            resp = enabledCommands[intent] + f'@{authors}'
            retResp.append(resp)
    else:
        resp = enabledCommands[intent]
        retResp.append(resp)
    
    return retResp

def updateFunc(content):
    splitCommand = content.split(maxsplit=2)
    if splitCommand[0] == '!update' and splitCommand[1] in enabledCommands:
        currentMsg = enabledCommands[splitCommand[1]]
        enabledCommands[splitCommand[1]] = splitCommand[2]
        msg = 'Updated Autoreply for '+ splitCommand[1] + ' from ' + currentMsg + ' to ' + splitCommand[2]
        return msg
    else:
        return 'Incorrect format: use \'!update <command to update> <new message>\''

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

def systemTest():
    print('Input stopTest to end test environment and close program')
    while True:
        testMsg = input()
        if testMsg == 'stopTest':
            break
        if testMsg[0] == '!':
            msg = updateFunc(testMsg)
            print(msg)
        
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
#add non connected chat service for testing
#record video
#finish submission
#Finish racism detection functionality and add more banter test cases for banter detection
#add more detections