# Basic bot to post RCQ schedule

import os
import time

import discord

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Load our discord room name and token from a .env file on disk in this folder
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Currently connecting and reading messages in chat looking for the word "rcqs" to respond to
# Probably better to just put everything in on ready and have it update once per run
# Then I can just put the script in my startup folder and it will update the screenshot each time I turn on the PC
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if "rcqs" in message.content.lower():
        options = Options()
        service = Service(executable_path=ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=options)
        # Query has location to centre on, event type (i.e. RCQ) and distance into the future to look hard coded in it currently
        # NORWICH Centered - 50 miles
        # query="https://www.spicerack.gg/events?formats=&eventTypes=regional_championship_qualifier&rulesEnforcementLevels=&numMiles=50&numDays=180&latitude=52.57218&longitude=1.3396542&selectedStores=&selectedStates=&page_size=25"
        # SHAFTESBURY Centered - 100 miles
        query="https://www.spicerack.gg/events?formats=&eventTypes=regional_championship_qualifier&rulesEnforcementLevels=&numMiles=100&numDays=180&latitude=51.0046&longitude=-2.198083&selectedStores=&selectedStates=&page_size=25"

        # Make the request to the website - wait a few seconds for them to service it
        # 3 second sleep seems fine but almost certainly some method available for checking page load has finished
        browser.get(query)
        time.sleep(3)

        # Extract out the table of results
        # Assumes page we are looking up has the table we are interested in as the first on the page
        tables = browser.find_elements(By.TAG_NAME, "table")
        screenshot_path=r"C:\Users\Emilio\source\repos\rcq-bot\local_events.png"
        if len(tables) > 0:
            tables[0].screenshot(screenshot_path)
            msg = await message.channel.send("Local RCQs : ", file=discord.File(screenshot_path))
            await msg.pin()
        browser.quit()

client.run(TOKEN)
