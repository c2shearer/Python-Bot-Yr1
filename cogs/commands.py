import interactions
from interactions import *
import asyncio
from interactions.ext.wait_for import wait_for, setup
import re
GUILD_ID = 1020765433395163168

class Ping(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot
        
    @interactions.extension_listener()
    async def on_start(self):
        self.guild = await interactions.get(self.bot, interactions.Guild, object_id=GUILD_ID)
    @interactions.extension_command(name="ping", scope=GUILD_ID)
    async def PingCommand(self, ctx: interactions.CommandContext): 
        await ctx.send("🏓 Ping Pong!  {0}".format(round(self.bot.latency, 1)))
        
    
    @interactions.extension_command(name="changeperms", scope=GUILD_ID, default_member_permissions=interactions.Permissions.ADMINISTRATOR )
    async def changePerms(self, ctx):

        for channel in self.guild.channels:
            overwrites = [Overwrite(type=0, id=1025932940682739793, allow=66560),Overwrite(type=0, id=1020765433395163168, deny=66560),]
            await channel.modify(permission_overwrites=overwrites)
            await asyncio.sleep(0.2)
    
    
    @interactions.extension_command(name="makeannouncement", default_member_permissions=interactions.Permissions.ADMINISTRATOR, description="Make a *fancy* announcement", scope=GUILD_ID, options = [
                                                            interactions.Option(name="title",description="The title of the announcement", type=3, required=True ), 
                                                            interactions.Option(name="channel", description="The channel you want to send the announcemnt in", type=7,required=True),
                                                            interactions.Option(name="showauthor", description="Show who sent this announcemnt", required=False,type=5,),
                                                            interactions.Option(name="mentions", description="Mentions will be before the embed", required=False, type=3,),
                                                            interactions.Option(name="skipdesc", description="This will skip the description and go straight to adding a field", type=5,required=False)
                                                            ])
    async def makeAnnouncements(self, ctx: interactions.CommandContext, title: str, channel, showauthor=None, mentions=None, includeservericon=None, skipdesc=None):
        showauthor = False if showauthor is None else showauthor
        includeservericon = False if includeservericon is None else includeservericon
        skipdesc = False if skipdesc is None else skipdesc    
        async def waitForMessage():
            def check(m):
                print(m.content)

                return m.author.id == ctx.author.id and m.channel_id == ctx.channel.id

            try:
                message = await wait_for(self.bot,name='on_message_create', timeout=600, check=check)
            except asyncio.TimeoutError:
                await ctx.channel.send("Timed out.")
            return message

        await ctx.defer()
        await ctx.get_channel()
        if not skipdesc:
            delmessage = await ctx.channel.send(
                "Send a message of the content of this announcement! (You can use any text modifications such as **BOLD** and __underline__)")
            message = await waitForMessage()
            description = message.content
        else:
            description = ""
        embed = interactions.Embed(title=title, description=description)
        embed.color = 0x8018f0
        if showauthor:
            embed.set_footer(text=f"This announcement was made by {ctx.author.user.username}",
                                icon_url=ctx.author.user.avatar_url, )

        sendButton = interactions.Button(style=ButtonStyle.SUCCESS, label="Looks good! Send it!", custom_id="confirm")
        fieldButton = interactions.Button(style=ButtonStyle.PRIMARY, label="Add a new field", custom_id="field")
        delButton = interactions.Button(style=ButtonStyle.DANGER, label="Delete last field", custom_id="del", )
        cancelButton = interactions.Button(style=ButtonStyle.DANGER, label="Cancel", custom_id="cancel")
        row = [sendButton, fieldButton, delButton, cancelButton]
        actionrow = interactions.ActionRow(components=row)
        if not skipdesc:

            await message.delete()
            await delmessage.delete()

        embedMessage = await ctx.send(content="This is a preview of the message that will be sent in the channel.",
                                            embeds=embed, components=[actionrow])

        def check(button_ctx):
            print(button_ctx.author.id == ctx.author.id)
            return button_ctx.author.id == ctx.author.id
        buttonCtx: ComponentContext = await self.bot.wait_for_component(components=row,check=check)
        confirmed = False
        while not confirmed:
            await buttonCtx.defer(edit_origin=True)

            if not skipdesc:
                if buttonCtx.custom_id == "confirm" and buttonCtx.author.id == ctx.author.id:
                    await channel.send(content=mentions, embeds=embed)
                    await buttonCtx.edit(embeds=None, content="Sent!", components=None)
                    confirmed = True
                    return
                elif buttonCtx.custom_id == "cancel" and buttonCtx.author == ctx.author:
                    await buttonCtx.edit(embeds=None, content="Cancelled", components=None)
                    return
                elif buttonCtx.custom_id == "field" and buttonCtx.author.id == ctx.author.id :
                    delMessage = await ctx.channel.send("What is the title of the field?")
                    message = await waitForMessage()
                    name = message.content
                    await message.delete()
                    await asyncio.sleep(0.1)
                    await delMessage.delete()
                    delMessage = await ctx.channel.send("What is the content of the field?")
                    message = await waitForMessage()
                    value = message.content
                    await message.delete()
                    await asyncio.sleep(0.1)
                    await delMessage.delete()
                    embed.add_field(name=name, value=value, inline=False)

                    await buttonCtx.edit(embeds=embed)
                elif buttonCtx.custom_id == "del" and buttonCtx.author.id == ctx.author.id:
                    index = len(embed.fields) -1
                    embed.remove_field(index)
                    await buttonCtx.edit(embeds=embed)
                    

            else:

                delMessage = await ctx.channel.send("What is the title of the field?")
                message = await waitForMessage()
                name = message.content
                await message.delete()
                await asyncio.sleep(0.1)
                await delMessage.delete()
                delMessage = await ctx.channel.send("What is the content of the field?")
                message = await waitForMessage()
                value = message.content
                await message.delete()
                await asyncio.sleep(0.1)
                await delMessage.delete()
                embed.add_field(name=name, value=value)

                embedMessage = await ctx.send(content="This is a preview of the message that will be sent in the channel.",embeds=embed, components=[actionrow], )
                skipdesc = False


            buttonCtx: ComponentContext = await self.bot.wait_for_component(components=row)   
        

def setup(bot):
    Ping(bot)
