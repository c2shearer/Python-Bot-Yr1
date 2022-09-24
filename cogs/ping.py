import interactions

GUILD_ID = 1020765433395163168

class Ping(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot
     
    @interactions.extension_command(name="ping", scope=GUILD_ID)
    async def PingCommand(self, ctx: interactions.CommandContext): 
        await ctx.send("🏓 Ping Pong!  {0}".format(round(self.bot.latency, 1)))

def setup(bot):
    Ping(bot)