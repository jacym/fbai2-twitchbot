# Wit AI AutoModerator For Twitch
An automated moderator service using Wit AI for Twitch live chat. Initially built for Facebook Hackathon.

## Setup
### Full Twitch Setup
#### Requirements:
- Python 3.8
- A Twitch account authorized to create bots
- Your Twitch OAuth token

Your pipenv .env file should contain the following information:
```
# .env
TMI_TOKEN=oauth: YOUR TWITCH OAUTH TOKEN
CLIENT_ID= YOUR TWITCH CLIENT ID
BOT_NICK=BOT NICK NAME
BOT_PREFIX=!
CHANNEL=CHANNEL TO RUN BOT
WIT_TOKEN= WIT AI TOKEN
```
TMI_TOKEN can be found at https://twitchapps.com/tmi/
CLIENT_ID can be found after you create an app on your Twitch account.

Then run the bot using:
`pipenv run python Autobot.py run`

### Cmd Line Chat Test Setup
If the goal is just to try out the automod functionality without connecting to a Twitch chat simply fill in the above .env file with lorem ipsum data except for the Wit token.

Then run the bot using:
`pipenv run python Autobot.py test`

This will create a command line chat for you to emulate a chat experience and demonstrate the automod capabilities.

