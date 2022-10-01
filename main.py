
import asyncio
#from interactions.ext import wait_for
#from interactions.ext.wait_for import setup
from dotenv import load_dotenv

from interactions.ext.wait_for import setup
import interactions
import os
from threading import Thread

import sqlite3

import logging
import logging.handlers

import config

def loadExtentions(bot):
    logger = logging.getLogger('bot')
    logger.debug("========================RESTART===========================")

    cfg = config.Get()
    extentions = cfg["cogs"]

    for ext in extentions:
        try:
            bot.load("cogs." +ext)
            print(ext)
        except Exception as e:
            logger.critical(f"Error loading {ext}: ({e})")
            print(f"Error loading {ext}: ({e})")
def setupLogging():
    logger = logging.getLogger('bot')
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.TimedRotatingFileHandler(filename="resources/logs/bot.log", when="h", interval=8, backupCount=3,encoding = "utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    logger.addHandler(handler)
    #logging.basicConfig(level=-1)

    
def main():
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    intents = interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT
    bot = interactions.Client(TOKEN,disable_sync=False,intents=intents)
    setup(bot)
    #setupLogging()


    loadExtentions(bot)
    print("starting....")

    bot.start()





if __name__ == "__main__":
    #logging.basicConfig(level=-1)
     main()
    
