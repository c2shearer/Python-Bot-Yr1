# TESTING COMMAND

from interactions import *

class Ping(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot;

    async def PingCommand(ctx: interactions.CommandContext): 
        await ctx.send("🏓 Ping Pong!  {0}".format(round(bot.latency, 1)))

def setup(bot):
    Ping(bot)