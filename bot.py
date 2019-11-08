import os
import discord
from message import MessageProcessor
from dotenv import load_dotenv


# load .env file
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path=dotenv_path)

# get bot token
TOKEN = os.getenv('BOT_TOKEN')

# create a client
client = discord.Client()


@client.event
async def on_message(message):
    """
    When message received; invoke message processor which will process the message and
    generate response.
    """
    response = MessageProcessor().execute(message.content)
    if response:
        await client.send_message(message.channel, response)

@client.event
async def on_message_edit(before, after):
    """
    When message edited; invoke message processor which will process the message and
    generate response.
    """
    response = MessageProcessor().execute   (after.content)
    if response:
        await client.send_message(after.channel, response)

@client.event
async def on_ready():
    print("Chat bot: {} is ready now".format(client.user.name))

# run chat bot client
client.run(TOKEN)
