
import interactions
from interactions import *

GUILD_ID =1020765433395163168
class Roles(interactions.Extension):
    
    def __init__(self, bot):
        self.bot = bot
    
    
    
    @interactions.extension_command(name="sendcomponents", default_member_permissions=interactions.Permissions.ADMINISTRATOR, scope=GUILD_ID)
    async def sendComponentCommand(self, ctx):
        row = [interactions.Button(style=ButtonStyle.PRIMARY, label="Ping me for bot github updates!", custom_id="gitcom"),
]
        actionrow = interactions.ActionRow(components=row)
        await ctx.get_channel()
        await ctx.channel.send("We have a custom bot for this server, and **you can add features by submitting pull requests and adding your own code to the bot**. \nThe bot is in **python** and the library that is used is **interactions.py**. Its not a hard library to use, if you need any help with the library contact <@339866237922181121>\n\nRepository link: https://github.com/c2shearer/Python-Bot-Yr1 \nDocs for interactions.py: https://discord-interactions.readthedocs.io/en/latest/ ",components=[actionrow])
        
        
        



    @interactions.extension_listener()
    async def on_component(self, ctx):
        
        await ctx.get_guild()
        if ctx.custom_id == "CN":
            role = await ctx.guild.get_role(1021085196835094546)
        elif ctx.custom_id == "se":
            role = await ctx.guild.get_role(1021076439161909278)
        elif ctx.custom_id == "com":
            role = await ctx.guild.get_role(1021076473068666991)
        elif ctx.custom_id == "ds":
            role = await ctx.guild.get_role(1021085108809236510)
        elif ctx.custom_id == "csc":
            role = await ctx.guild.get_role(1021076502357483520)
        elif ctx.custom_id == "cs":
            role = await ctx.guild.get_role(1021084982434861126)
        elif ctx.custom_id == "gitcom":
            role = await ctx.guild.get_role(1021575482736648343)
        else:
            return
        try:
            if role is None: return
            if role.id in ctx.author.roles:
                await ctx.author.remove_role(role, ctx.guild.id)
                await ctx.send(content=f"I have removed the {role.name} role!", ephemeral=True, )
            else:
                await ctx.author.add_role(role, ctx.guild.id)
                await ctx.send(content=f"I have given you the {role.name} role!", ephemeral=True, )
        except Exception as e:
            print(e)
            
            

def setup(bot):
    Roles(bot)