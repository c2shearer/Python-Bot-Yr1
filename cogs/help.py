
import sqlite3
import asyncio
import logging
from dotenv import load_dotenv
import logging.handlers
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import interactions
from interactions.api.models.misc import Overwrite
import io
import os
import re
import json
import config
from datetime import timedelta
from datetime import datetime
cooldownTime = 30
logger = logging.getLogger("bot")
from interactions.ext.tasks import create_task, IntervalTrigger
helpChannelNames = ["Ash", "Birch", "Cedar", "Dragon", "Elm", "Fir","Garjan", "Hazel", "Ivorypalm", "Juniper", "Kapok", "Locust", "Mombin","Nutmeg", "Oak", "Palm","Sapel", \
                    "Teak", "Upas", "Wingnut", "Yew", "Zelkova" ] 
BASE_REWARD = 250

cfg = config.Get();
guild_id = cfg["general"]["guild_id"]

HELP_CHANNELS = [1024112753046208642,1024112754803613748,1024112756552634479,1024112758758846565,1024112760839217254,1024112762588246026,1024112764916080660, \
    1024112766946136115,1024112768749682698,1024112770213482659, 1024112772272889997, 1024112774219046932, 1024112776026800128, 1024112777918418944, 1024112779776507914,
    1024112779776507914,1024112783945633862, 1024112785862443058, 1024112787682754570,1024112789922533486,1024112791981920367, 1024112793760309288]
cdRole = 1023272185365803120
avaliable = 1021480541444386977
dormant = 1021480689557848064
default_role = guild_id
occupiedChannels = (("Computer Science", 1023280589106847796), ("Software Engineering", 1023281071074324520), ("Cyber Security", 1021480634616643654), ("Networking", 1023280720833171546),("Data Science", 1023281235507814461))
helpRoles = (1023272369919369397,1023272366656208977,1023272353104400424,1023272346762629141,1023272346762629141,1023272335660302487,1023272328248971335)
host = "localhost"
host = "212.111.42.251"
load_dotenv()

USER = os.getenv("MYSQL_USER")
PASSWD  = os.getenv("MYSQL_PASS")

def connect(host):
    global con
    con = mysql.connector.connect(
        host=host,
        user=USER,
        passwd=PASS,
        database="FYdatabase"
    )
    cur = con.cursor(buffered=True)
    return cur
class Help(interactions.Extension):
        def __init__(self, bot):
            self.bot = bot
            self.questions = {}
            self.guild = None
            self.cdRole = None
            #with open("resources/databases/questions.json", "r") as F:
                #self.questions = json.load(F)
            
        
        @interactions.extension_listener()
        async def on_start(self):
            self.guild = await interactions.get(self.bot, interactions.Guild, object_id=guild_id)
            self.cdRole = await interactions.get(self.bot, interactions.Role, object_id=1023272185365803120, parent_id=guild_id)
            self.channelExpiration.start(self)
        @interactions.extension_command(name="deletechannels", scope=guild_id,default_member_permissions=interactions.Permissions.ADMINISTRATOR)
        async def deleteChannels(self,ctx):
            await ctx.defer()
            channels = await self.getCatChannels(dormant)
            print(channels)
            for channel in channels:
                await channel.delete()
                await asyncio.sleep(0.2)
        
        
        @interactions.extension_command(name="createchannels", scope=guild_id,default_member_permissions=interactions.Permissions.ADMINISTRATOR)
        async def createChannels(self, ctx):
            await ctx.defer()
            overwrites = [Overwrite(id=default_role, type=0, deny=2048)]
            for word in helpChannelNames: # creates 26 channels with different tree names
                
                name ="help-" + word.lower() # etc help-oak
                
                channel = await self.guild.create_channel(name=name, topic=f"The {word} help channel", permission_overwrites=overwrites, type=interactions.api.models.channel.ChannelType.GUILD_TEXT, parent_id=dormant)
                
                avaliableEmbed = interactions.Embed(title="This help channel is avaliable!", description="To claim this help channel type (SUBJECT) then your question after. \
                                            For example: \n\n*(COMPUTER SCIENCE) Are dictionaries in python ordered or unordered?*\n\n Alternatively, if your question isnt tied to a subject just add (GENERAL)  \
                                                before your question for example:\n\n*(GENERAL) Where is the assembly today taking place?*\n\n hopefully someone can help!", colour=0x3ee800)
                dormantEmbed = interactions.Embed(title="This help channel is dormant.", description="If you need help look at the avaliable channels category for more do the \
                    command /howtogethelp!", colour = 0xff2b2b)
                await asyncio.sleep(0.2)

                
            channels = await self.getCatChannels(dormant)
            for x in range(3): # This will move 3 channels from dormant to avaliable category and send the avaliable embed.
                channels = await self.getCatChannels(dormant)
                channel= channels[0]
                await channel.modify(parent_id=avaliable, permission_overwrites=overwrites)
                await channel.send(embeds=avaliableEmbed)
                await asyncio.sleep(0.2) # A little bit of delay so discord doesnt rate limit us.
            channels = await self.getCatChannels(dormant)
            for channel in channels: #The rest of the channel we will send the dormant embed
                await channel.send(embeds=dormantEmbed)
                await asyncio.sleep(0.2)                
        @interactions.extension_command(name="exp", scope=guild_id, default_member_permissions=interactions.Permissions.ADMINISTRATOR, description="Describes how to get help", options = [interactions.Option(name="member", description="The person you want to give exp",required=True, type=interactions.OptionType.USER),
interactions.Option(name="amount", description="The amount of exp",required=True, type=interactions.OptionType.INTEGER)])
        async def exp(self, ctx, member, amount):
            if amount > 0:
                await self.addExp(member, amount, ctx.guild, False)
                await ctx.send(f"{amount} exp added!")
            else:
                await ctx.send("You cant add negative or 0 exp!!")
        @interactions.extension_command(name="howtogethelp", scope=guild_id, description="Describes how to get help")
        async def howToGetHelp(self, ctx):
            await ctx.get_guild()
            channel = ctx.guild.get_channel(int(id))
            file = interactions.File("resources/images/htgh.gif", "htgh.gif")
            embed = interactins.Embed(title="Understanding the help channels", description="The help system tries to make it easier for students to get help from other students or teachers. To get help using the help channel system you must:\n **1.** Find an avaliable help channel, \
                                                                                    avaliable help channels are in the **\"{0}\"** category. You will know when its avaliable when the message on the channel  \
                                                                                        says it is.\n**2.** When found you can claim the help channel!, to do this you must specify what subject you need help with by typing (SUBJECT) before then ask your question!. Make sure the subject \
                                                                                            you type is a subject your school offers by doing /subjects.\n**3.** Play the waiting game and wait for another student or a teacher to help! Students are rewarded with cosmetic roles for helping in \
                                                                                                 these channels. Maybe you can help in a subject that your confident in by checking if the category for that subject \
                                                                                                    The more people you help the more cosmetic roles you get and helping people is just nice for your school community\nThere is an example below\n\n**NOTE:** Help channels are automatically \
                                                                                                        closed after 30 minutes of inactivity. You can close it whenever you want with /close though.".format(channel.name))
            embed.set_image(url="attachment://htgh.gif")                                                                         
            
            await ctx.send(embed=embed, file=file)
            
        @interactions.extension_command(name="selfishclose",scope=guild_id, description="Closes the current help channel without rewarding anyone :(")
        async def selfishClose(self, ctx):
            await ctx.get_channel()
            if int(ctx.channel.id) in HELP_CHANNELS:
                
                message = await ctx.channel.get_pinned_messages()
                #message = message[0]
                if ctx.author.id == ctx.author.id:

                    #await message.unpin()
                    await ctx.send("Closing help channel.")
                    await self.markAsDormant(ctx.channel)
                else:
                    await ctx.send("You can't close someone elses help channel!")
            else:
                await ctx.send("This isn't a help channel")
        @interactions.extension_command(name="close",scope=guild_id, description="Closes the current help channel",options=[ 
                                                                                interactions.Option(name="helper",description="Specify the person who helped you",required=True,type=interactions.OptionType.USER),
                                                                                interactions.Option(name="rating",description="How much did this person help you? 1-10",required=False,type=interactions.OptionType.INTEGER)])
        async def close(self, ctx, helper, rating=None):
            global BASE_REWARD
            rating = 5 if rating is None else rating
            if rating <1 or rating >10:
                await ctx.send("Thats not a rating between 1 and 10!")
                return
            await ctx.get_guild()
            cur.execute(f"SELECT * FROM helpLevels WHERE memberId = {helper.id}")
            if cur.fetchone() is None:
                cur.execute("INSERT INTO helpLevels VALUES (?,?,?,?)", (helper.id, 0,0,1))
                record = (helper.id,0,0,1)
            else:
                record = cur.fetchone()

            if int(ctx.channel.id) not in HELP_CHANNELS:
                helpers = self.questions[str(ctx.channel.id)]["helpers"]
                if str(helper.id) not in helpers.keys():
                    await ctx.send("This person did not help you!")
                    return
                
                message = await ctx.channel.pins()
                message = message[0]
                if message.author.id == ctx.author.id:

                    await message.unpin()
                    await ctx.send("Closing help channel.")
                    rating /= 10
                    rating+=0.3
                    multiplier =1+rating if rating >0.5 else 1-rating
                    amount = BASE_REWARD*multiplier if rating != 0.5 else BASE_REWARD
                    await self.addExp(helper, amount, ctx.guild)
                    await self.markAsDormant(ctx.channel)
                else:
                    await ctx.send("You can't close someone elses help channel!")
            else:
                await ctx.send("This is not a help channel!")
        @interactions.extension_command(name="rank",scope=guild_id, description="Specifies the rank of you or another member", options=[interactions.Option(name="member",description="You can specify a member you want to see the rank of",required=False,type=interactions.OptionType.USER)])
        async def rank(self, member=None):
            if member is None:
                member = ctx.author

            cur.execute(f"SELECT * FROM helpLevels WHERE memberId = {member.id} AND guildId = {ctx.guild.id}") # fetching the rank info for the user
            record = cur.fetchone()
            if record is None:
                cur.execute("INSERT INTO helpLevels VALUES(?,?,?,?,?)", (member.id,0,0,1))
                record = (member.id, ctx.guild.id, 0,0,1)

            buffer = await self.getRankImage(member, record[2], record[4], record[3], ctx.guild)
            await ctx.send(file=File(buffer, "rank.png"))


        async def getCatChannels(self, parent):
            channelArr = await self.guild.get_all_channels()
            channels = []
            for channel in channelArr:
                if channel.parent_id == parent:
                    channels.append(channel)
            
            return channels
        async def getOccupiedChannels(self):
            channels = []
            for channel in occupiedChannels:
                chanList = await self.getCatChannels(channel)
            
                channels+=chanList
            return channels
                
        @interactions.extension_listener()
        async def on_message_create(self, msg): # Everytime a message is sent in a channel the bot can see
            occChannels = await self.getOccupiedChannels()
            member = await interactions.get(self.bot, interactions.Member, object_id=msg.author.id, parent_id=guild_id)

            channel = await interactions.get(self.bot, interactions.Channel, object_id=msg.channel_id)
            now = datetime.utcnow() # Timezones don't matter since we are just using the time to see how long a help channel is open.
            
            if int(channel.id) not in HELP_CHANNELS: # Checking if the channel is a help channel
                
                return
            else:
                guild = self.guild
                

          
                avaliableOb = await interactions.get(self.bot, interactions.Channel, object_id=avaliable)
                dormantOb = await interactions.get(self.bot, interactions.Channel, object_id=dormant)
                

                if channel.parent_id == avaliable: # This means a message was sent in an avaliable help channel
                    logger.debug("Recognised avaliable channel")
                    msgList = msg.content.split()
                    try:
                        prefix = msgList[0] +" " +msgList[1]# The first word should be the subject (COMPUTER SCIENCE)
                    except:
                        return
                    subMatch = re.search("\((\D+)\)", prefix)  # Checking if the first word of the sentence is (WORD) so the person has the right syntax
                    print(prefix)
                    if subMatch: #If it matches
                        print("hi")
                        sub = subMatch.group(1)
                       
                        subject = None
                        for x in range(len(occupiedChannels)):
                            if occupiedChannels[x][0].lower() == sub.lower():
                                subject = occupiedChannels[x]

                            else:
                                continue
                            
                        if subject is not None:
                            await msg.pin() ##pinning a message is like "bookmarking" a message a list of pinned messages can be seen in the channel
                          
                            subcat = subject[1]# Gets the subject category
                            overwrites = [Overwrite(id=cdRole, type=0, allow=67584)]# People on cool down will be able to see the occupied help channel in case they want to help

                            await channel.modify(permission_overwrites=overwrites, parent_id=subcat)  #Moves the channel to its subject category
             
                            sub = sub.lower()
                            embed = interactions.Embed(title="Help channel claimed!", description = f"You claimed the help channel {channel.mention} for the subject {sub}")
                            embed.add_field(name="Your question", value=msg.content, inline=False)
                            
                            link = "https://www.discord.com/channels/" + str(guild.id) +"/"+ str(channel.id) +"/" + str(msg.id) # Link to the message
                            embed.add_field(name="Link to message", value =f"[Click here to jump to your question]({link})")


                            await member.send(embeds=embed) #Sends a direct message to the person claiming the channel with all the info
                            self.questions[str(int(channel.id))] = {}
                            self.questions[str(int(channel.id))]["owner"] = int(msg.author.id)
                            self.questions[str(int(channel.id))]["lastMessage"] = [now.year, now.month, now.day, now.hour, now.minute]
                            self.questions[str(int(channel.id))]["messageId"] = int(msg.id)
                            self.questions[str(int(channel.id))]["helpers"] = {}
                            print(self.questions)
                            with open("resources/questions.json", "w") as F: # In case the bot goes down while this is running we store it in a file
                                
                                json.dump(self.questions, F)
                            dormantChannels= await self.getCatChannels(dormant)
                            newAvaliableChannel = dormantChannels[0] #Selects the next dormant channel that is ready to be moved to avaliable
                            #await newAvaliableChannel.modify(permission_overwrites=[Overwrite(id=cdRole, type=0, deny=65536), Overwrite(id=1020765433395163168, type=0, deny=67584)])  # Students should be allowed to send messages and avaliable channels should be hidden to people with the cooldown role
                            
                            avaliableEmbed = interactions.Embed(title="This help channel is avaliable!", description="To claim this help channel type (SUBJECT) then your question after. \
                                                            For example: \n\n*(COMPUTER SCIENCE) Are dictionaries in python ordered or unordered?*\n\n Alternatively, if your question isnt tied to a subject just add (GENERAL)  \
                                                                before your question for example:\n\n*(GENERAL) Where is the assembly today taking place?*\n\n hopefully someone can help!", colour=0x3ee800)
                            await newAvaliableChannel.modify(permission_overwrites=overwrites)
    
                            await newAvaliableChannel.modify(parent_id=avaliable)
                            await newAvaliableChannel.send(embeds=avaliableEmbed)
                            await self.cooldown(msg.author)
                        else:
                           
                            await member.send("That is not a subject the school has registered! If you believe this is in error tell managers to add this subject.")
                            await msg.delete()
                           
                    else:
                        await msg.delete()
                        await member.send("Make sure you put the subject name before your question! For example:\n\n (Software engineering) How can I use the binomial infinite series to estimate pi? \n\n")
                elif channel.parent_id in occChannels:

                    self.questions[str(channel.id)]["lastMessage"] = [now.year, now.month, now.day, now.hour, now.minute]
                    
                    if str(msg.author.id) not in self.questions[str(msg.channel.id)]["helpers"].keys():
                        self.questions[str(channel.id)]["helpers"][str(msg.author.id)] = 1
                    else:
                        self.questions[str(channel.id)]["helpers"][str(msg.author.id)] +=1
                    
                    with open("resources/databases/questions.json", "w") as F:
                        json.dump(self.questions, F)


                            
                else:
                    pass
                    
                
                    
                    
                


        @create_task(IntervalTrigger(delay=60))
        async def channelExpiration(self):
            deleteList = [] 
            global BASE_REWARD
            for k, v in self.questions.items():
                print(v)
                lastMessageDate = datetime(v["lastMessage"][0],v["lastMessage"][1],v["lastMessage"][2],v["lastMessage"][3],v["lastMessage"][4])
                
                expire = datetime.utcnow() + timedelta(minutes=2)
                conditions = [lastMessageDate.year == expire.year, lastMessageDate.month == expire.month, lastMessageDate.day == lastMessageDate.day, lastMessageDate.hour == expire.hour, lastMessageDate.minute == expire.minute]
                if all(conditions):

                    print(lastMessageDate)
                    print(expire)
                    deleteList.append(k)
                    helpers = v["helpers"]
                    if len(helpers) == 0:
                        pass
                    else:
                        highest = 0
                        for k, v in helpers.items():
                            if v > highest:
                                helper = k
                                highest = v
                    helper = guild.get_member(helper)                       
                    rating /= 10
                    rating+=0.3
                    multiplier =1+rating if rating >0.5 else 1-rating
                    amount = BASE_REWARD*multiplier if rating != 0.5 else BASE_REWARD
                    await self.addExp(helper, amount, ctx.guild)
                    channel = self.bot.get_channel(int(k))
                    message = await channel.fetch_message(int(v["messageId"]))
                    guild = message.guild
                    await message.unpin()
                    await self.markAsDormant(channel)
                
            for k in deleteList:
                del self.questions[k]

        async def cooldown(self, member):
            global cooldownTime
            
            await self.guild.add_member_role(role=self.cdRole, member_id=member.id)
            await asyncio.sleep(cooldownTime)
            await self.guild.remove_member_role(role=self.cdRole, member_id=member.id)

        async def markAsDormant(self, channel): # This is to mark a channel as dormant
            
            valid = False
            print(channel.id)
            if int(channel.id) not in HELP_CHANNELS:
                raise ValueError("Channel is not in help_channels")
        
            dormantEmbed = interactions.Embed(title="This help channel is dormant.", description="If you need help look at the avaliable channels category for more do the \
                                command /howtogethelp!", colour = 0xff2b2b)         
            await channel.send(embeds=dormantEmbed)
            overwrite = [Overwrite(id=default_role,type=0, allow=2048),Overwrite(id=default_role,type=0, allow=2048)]

            await channel.modify(permission_overwrites=overwrite, parent_id=1021480689557848064)




        async def addExp(self, helper, amount, guild, natural=True):
            global BASE_REWARD
            
            cur.execute(f"SELECT * FROM helpLevels WHERE memberId = {helper.id}")
            record = cur.fetchone()
            if record is None:
                cur.execute("INSERT INTO helpLevels VALUES (?,?,?,?,?)", (helper.id, guild.id, 0,0,1))
                record = (helper.id, guild.id, 0,0,1)

                
                
            exp = record[2]
            exp+=amount
            level = baseLevel = record[4]
            helped = record[3]
            if natural:
                helped+=1
            leveledUp=False
            while exp >= 1000:
                level +=1
                exp -=1000
                leveledUp = True
            levelDifference = level - baseLevel 
            if leveledUp:

                await helper.create_dm()
                name = helper.name + helper.discriminator
                buffer = await self.getRankImage(helper,  exp, level,helped, guild)
                embed = discord.Embed(title="You leveled up!", description=f"You are now level **{level}**", colour=0x00FF00)
                embed.set_thumbnail(url=helper.avatar_url)

                await helper.dm_channel.send(embed=embed)
                
                if level//10 == 0 and level <=100:
                    
                    if levelDifference >10:
                        removeIndex = int((baseLevel//10)-1)
                        index = int((level//10)-1)
                        removeRole = guild.get_role(int(helpRoles[removeIndex][0]))
                        role = guild.get_role(int(helpRoles[index][0]))
                        await helper.remove_roles(removeRole)
                        await helper.add_roles(role)

                        
                    else:
                        index = (level/10)-1
                        role = roles[index][0]
                        if index == 0:
                            pass
                        else:
                            removeRole = guild.get_role(roles[index-1][0])
                            await helper.remove_roles(removeRole)
                    
                        role = guild.get_role(role)
                        await helper.add_roles(role)



            cur.execute(f"UPDATE helpLevels SET exp = {exp}, peopleHelped = {helped}, level = {level} WHERE helperId = {helper.id}", )



        async def getRankImage(self,member, exp,  level, guild):
                def drawProgressBar(d, x, y, w, h, progress, bg="black", fg="#a400fc"):
                    # draw background
                    d.ellipse((x+w, y, x+h+w, y+h), fill=bg)
                    d.ellipse((x, y, x+h, y+h), fill=bg)
                    d.rectangle((x+(h/2), y, x+w+(h/2), y+h), fill=bg)

                    # draw progress bar
                    w *= progress
                    d.ellipse((x+w, y, x+h+w, y+h),fill=fg)
                    d.ellipse((x, y, x+h, y+h),fill=fg)
                    d.rectangle((x+(h/2), y, x+w+(h/2), y+h),fill=fg)
                rank = await guild.get_role(ranks[level][1])
                if level == 5:
                    nextRank =None
                else:
                    nextRank = await guild.get_role(ranks[level+1][1])

                def conv(num):
                    blue =  num & 255
                    green = (num >> 8) & 255
                    red =   (num >> 16) & 255
                    return (red, green, blue)   
                rankColour = conv(rank.color)

                
                size = width, height = 900, 200
                image = PIL.Image.new("RGB", size, "#342e38")
                image = image.convert("RGBA")

                
                font = PIL.ImageFont.truetype("resources/Fonts/impact.ttf",40)
                rankfont = PIL.ImageFont.truetype("resources/Fonts/light.ttf",30)
                titlefont = PIL.ImageFont.truetype("resources/Fonts/med.ttf",27)
                draw = PIL.ImageDraw.Draw(image)
                draw.rounded_rectangle([10, 20, width-10, height-20], fill=(74,74,74, 200), width=3,radius=20)
                response = requests.get(member.user.avatar_url)
                buffer_avatar = io.BytesIO(response.content)
                buffer_avatar.seek(0)
                threashold = 1000 + level*500
                progress=exp/threashold if nextRank is not None else 1
                # read JPG from buffer to Image
                avatar_image = PIL.Image.open(buffer_avatar)
                avatar_image = avatar_image.resize((128,128))
                circle_image = PIL.Image.new("L", (128, 128))
                circle_draw = PIL.ImageDraw.Draw(circle_image)
                circle_draw.ellipse((0,0, 128,128), fill=255)
                image.paste(avatar_image, (20,35), circle_image)
                name = member.user.username + "#" + member.user.discriminator
                draw.multiline_text((175,35), name, font=font, fill=(0, 166, 255))
                draw.multiline_text((175,90), rank.name, font=titlefont, fill=rankColour)
                #draw.multiline_text((662,50), f"RANK: #1", font=rankfont, fill=(0, 166, 255) ) 
                if nextRank is not None:
                    nextRankColour = conv(nextRank.color)
                    draw.multiline_text((700,100), nextRank.name, font=titlefont, fill=nextRankColour)
                    draw.multiline_text((790,135), f"{exp}/{threashold}", font=titlefont, fill=nextRankColour)
                else:
                    draw.multiline_text((790,135), f"Max rank!", font=titlefont, fill=(235, 30, 30) )
                    nextRankColour = (235, 30, 30)
                #draw.multiline_text((662,130), f"People helped: {total}", font=rankfont, fill=(0, 166, 255))

                draw = drawProgressBar(d=draw, x=155,y=135, w=600, h=25, progress=progress, fg='#%02x%02x%02x' % rankColour)
                image.resize((1350,300))
                buffer_output = io.BytesIO()
                image.save(buffer_output, "PNG")
                buffer_output.seek(0)
                return buffer_output






    
def setup(bot):
    Help(bot)
