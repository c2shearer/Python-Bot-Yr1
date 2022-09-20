
import sqlite3
import asyncio
import logging
import logging.handlers
import discord_slash
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import interactions
from interactions import *
import io
import json
from datetime import timedelta
from datetime import datetime
cooldownTime = 30
logger = logging.getLogger("bot")
con = sqlite3.connect("resources/databases/schooldata.db")
cur = con.cursor()
BASE_REWARD = 250
guild_ids = [1020765433395163168]
HELP_CHANNELS = []
class Help(interactions.Extension):
        def __init__(self, bot):
            self.bot = bot
            self.questions = {}

            #with open("resources/databases/questions.json", "r") as F:
                #self.questions = json.load(F)
            
            self.channelExpiration.start()
        @cog_ext.cog_slash(name="exp", guild_ids=guild_ids, description="Describes how to get help", options = [create_option(name="member", description="The person you want to give exp",required=True, option_type=6),
                                                                                                                    create_option(name="amount", description="The amount of exp",required=True, option_type=4)])
        async def exp(self, ctx, member, amount):
            if amount > 0:
                await self.addExp(member, amount, ctx.guild, False)
                await ctx.send(f"{amount} exp added!")
            else:
                await ctx.send("You cant add negative or 0 exp!!")
        @interactions.extension_command(name="howtogethelp", guild_ids=guild_ids, description="Describes how to get help")
        async def howToGetHelp(self, ctx: discord_slash.SlashContext):
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
            
        @interactions.extension_command(name="selfishclose",guild_ids=guild_ids, description="Closes the current help channel without rewarding anyone :(")
        async def selfishClose(self, ctx):
            await ctx.get_channel()
            if ctx.channel.id not in HELP_CHANNELS:
                
                message = await ctx.channel.get_pinned_messages()
                message = message[0]
                if message.author.id == ctx.author.id:

                    await message.unpin()
                    await ctx.send("Closing help channel.")
                    await self.markAsDormant(ctx.channel)
                else:
                    await ctx.send("You can't close someone elses help channel!")
            else:
                await ctx.send("This isn't a help channel")
        @interactions.extension_command(name="close",guild_ids=guild_ids, description="Closes the current help channel",options=[ 
                                                                                interactions.Option(name="helper",description="Specify the person who helped you",required=True,option_type=6),
                                                                                interactions.Option(name="rating",description="How much did this person help you? 1-10",required=False,option_type=4)])
        async def close(self, ctx: discord_slash.SlashContext, helper, rating=None):
            global BASE_REWARD
            rating = 5 if rating is None else rating
            if rating <1 or rating >10:
                await ctx.send("Thats not a rating between 1 and 10!")
                return
            await ctx.get_guild()
            cur.execute(f"SELECT * FROM helpLevels WHERE memberId = {helper.id} AND guildId = {ctx.guild.id}")
            if cur.fetchone() is None:
                cur.execute("INSERT INTO helpLevels VALUES (?,?,?,?,?)", (helper.id, ctx.guild.id, 0,0,1))
                record = (helper.id, ctx.guild.id, 0,0,0)
            else:
                record = cur.fetchone()

            if ctx.channel.id not in HELP_CHANNELS:
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
        @interactions.extension_command(name="rank",guild_ids=guild_ids, description="Specifies the rank of you or another member", options=[create_option(name="member",description="You can specify a member you want to see the rank of",required=False,option_type=6)])
        async def rank(self, ctx: discord_slash.SlashContext, member=None):
            if member is None:
                member = ctx.author

            cur.execute(f"SELECT * FROM helpLevels WHERE memberId = {member.id} AND guildId = {ctx.guild.id}")
            record = cur.fetchone()
            if record is None:
                cur.execute("INSERT INTO helpLevels VALUES(?,?,?,?,?)", (member.id, ctx.guild.id, 0,0,1))
                record = (member.id, ctx.guild.id, 0,0,1)

                
            print(record)
            buffer = await self.getRankImage(member, record[2], record[4], record[3], ctx.guild)
            await ctx.send(file=File(buffer, "rank.png"))

        @commands.Cog.listener()
        async def on_ready(self):
            logger.debug("Help cog is ready!")

        @commands.Cog.listener() # bot event
        async def on_message(self, msg): # Everytime a message is sent in a channel the bot can see
           
            now = datetime.utcnow() # Timezones don't matter since we are just using the time to see how long a help channel is open.
            cur.execute("SELECT guild_id FROM help_channels WHERE channel_id = ?", (msg.channel.id,)) 
            guildId= cur.fetchone()
            
            if ctx.channel.id not in HELP_CHANNELS: # Checking if the channel is a help channel
                
                return
            else:
                guild = await self.bot.get_guild(guildId) #Gets the guild object from the Id
                channel = msg.channel # saves a little typing

          
                avaliable = guild.get_channel(record[1])  # Getting all the help categories
                dormant = guild.get_channel(record[0])
                cdRole = guild.get_role(record[2])
                cur.execute("SELECT category_id FROM subjects WHERE guildID = ?", (guild.id,)) #Gets all the subject categories
                
                channels = cur.fetchall() 
                occupiedChannels = [x[0] for x in channels] # List of occupied channels

                if msg.channel.category == avaliable: # This means a message was sent in an avaliable help channel
                    logger.debug("Recognised avaliable channel")
                    msgList = msg.content.split()
                    try:
                        prefix = msgList[0] # The first word should be the subject (COMPUTER SCIENCE)
                    except:
                        return
                    subMatch = re.match("\((\D+)\)", prefix)  # Checking if the first word of the sentence is (WORD) so the person has the right syntax
                    if subMatch: #If it matches
                        
                        sub = subMatch.group(1)

                        cur.execute("SELECT subject, category_id FROM subjects WHERE guildID= ?", (msg.guild.id,)) # Fetches the category
                        
                        subjects = cur.fetchall()
                       
                        subject = None
                        for x in range(len(subjects)):
                            if subjects[x][0].lower() == sub.lower():
                                subject = subjects[x]

                            else:
                                continue
                            
                        if subject is not None:
                            await msg.pin() ##pinning a message is like "bookmarking" a message a list of pinned messages can be seen in the channel
                          
                            subcat = guild.get_channel(subject[1]) # Gets the subject category
                            overwrites = {cdRole: discord.PermissionOverwrite(read_messages=True, send_messages=True)}# People on cool down will be able to see the occupied help channel in case they want to help

                            await msg.channel.edit(category=subcat, overwrites=overwrites)  #Moves the channel to its subject category
                            await msg.author.create_dm()
                            embed = discord.Embed(title="Help channel claimed!", description = f"You claimed the help channel {msg.channel.mention} for the subject {sub.lower()}")
                            embed.add_field(name="Your question", value=msg.content, inline=False)
                            
                            link = "https://www.discord.com/channels/" + str(guild.id) +"/"+ str(channel.id) +"/" + str(msg.id) # Link to the message
                            embed.add_field(name="Link to message", value =f"[Click here to jump to your question]({link})")


                            await msg.author.dm_channel.send(embed=embed) #Sends a direct message to the person claiming the channel with all the info
                            self.questions[str(msg.channel.id)] = {}
                            self.questions[str(msg.channel.id)]["owner"] = msg.author.id
                            self.questions[str(msg.channel.id)]["lastMessage"] = [now.year, now.month, now.day, now.hour, now.minute]
                            self.questions[str(msg.channel.id)]["messageId"] = msg.id
                            self.questions[str(msg.channel.id)]["helpers"] = {}
                            with open("resources/databases/questions.json", "w") as F: # In case the bot goes down while this is running we store it in a file
                                
                                json.dump(self.questions, F)
                            newAvaliableChannel = dormant.channels[0] #Selects the next dormant channel that is ready to be moved to avaliable
                            cur.execute("SELECT studentRoleId FROM schoolGuilds WHERE guildID = ?", (msg.guild.id,))
                            role =cur.fetchone()
                            sRole = msg.guild.get_role(role[0])
                           
                            overwrites = {
                            guild.default_role: discord.PermissionOverwrite(send_messages = False),
                            sRole: discord.PermissionOverwrite(send_messages=True),
                            cdRole: discord.PermissionOverwrite(read_messages=False)
                            }        # Students should be allowed to send messages and avaliable channels should be hidden to people with the cooldown role
                            
                            avaliableEmbed = discord.Embed(title="This help channel is avaliable!", description="To claim this help channel type (SUBJECT) then your question after. \
                                                            For example: \n\n*(COMPUTER SCIENCE) Are dictionaries in python ordered or unordered?*\n\n Alternatively, if your question isnt tied to a subject just add (GENERAL)  \
                                                                before your question for example:\n\n*(GENERAL) Where is the assembly today taking place?*\n\n hopefully someone can help!", colour=0x3ee800)
                            await newAvaliableChannel.edit(overwrites=overwrites)
    
                            await newAvaliableChannel.edit(category=avaliable)
                            await newAvaliableChannel.send(embed=avaliableEmbed)
                            await self.cooldown(msg.author, cdRole)
                        else:
                            await msg.author.create_dm()
                            await msg.author.dm_channel.send("That is not a subject the school has registered! If you believe this is in error tell managers to add this subject. To see a list of subjects in your school do /subjects")
                            await msg.delete()
                           
                    else:
                        await msg.delete()
                        await msg.author.create_dm()
                        await msg.author.dm_channel.send("Make sure you put the subject name before your question! For example:\n\n (MATHS) How can I use the binomial infinite series to estimate pi? \n\n")
                elif msg.channel.category.id in occupiedChannels:
                    print("hi")
                    self.questions[str(msg.channel.id)]["lastMessage"] = [now.year, now.month, now.day, now.hour, now.minute]
                    
                    if str(msg.author.id) not in self.questions[str(msg.channel.id)]["helpers"].keys():
                        self.questions[str(msg.channel.id)]["helpers"][str(msg.author.id)] = 1
                    else:
                        self.questions[str(msg.channel.id)]["helpers"][str(msg.author.id)] +=1
                    
                    with open("resources/databases/questions.json", "w") as F:
                        json.dump(self.questions, F)


                            
                else:
                    pass
                    
                
                    
                    
                


        @tasks.loop(seconds = 60)
        async def channelExpiration(self):
            deleteList = [] 
            global BASE_REWARD
            for k, v in self.questions.items():
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

        async def cooldown(self, member: discord.Member, cdRole: discord.Role):
            global cooldownTime
            await member.add_roles(cdRole)
            await asyncio.sleep(cooldownTime)
            await member.remove_roles(cdRole)

        async def markAsDormant(self, channel: discord.TextChannel): # This is to mark a channel as dormant
            
            cur.execute("SELECT guild_id, channel_id FROM help_channels")
            records = cur.fetchall()
            valid = False
            for g, c in records: # Guild, channel
                if c == channel.id: # checking if the channel stored in the database is the same as the channel given to the procedure?
                    valid = True
                    guild_id = g
                    break
            if not valid: # If there is no record of the channel in our list then we raise an error
                raise ValueError("Channel is not in help_channels")
        
            dormantEmbed = discord.Embed(title="This help channel is dormant.", description="If you need help look at the avaliable channels category for more do the \
                                command /howtogethelp!", colour = 0xff2b2b)         
            cur.execute("SELECT dormantCategoryId, avaliableCategoryId, cooldownRoleId FROM schoolGuilds WHERE guildID = ?", (guild_id,))
            guild = self.bot.get_guild(int(guild_id))
            record = cur.fetchone()
            dormant = guild.get_channel(record[0])
            avaliable = guild.get_channel(record[1])
            cdRole = guild.get_role(record[2])

            cur.execute("SELECT studentRoleId FROM schoolGuilds WHERE guildID = ?", (guild_id,))
            role = cur.fetchone()
            sRole = guild.get_role(int(role[0]))
            overwrites= {sRole: discord.PermissionOverwrite(read_messages=True, send_messages=False)}
            await channel.edit(category=dormant, overwrites=overwrites)
            await channel.send(embed=dormantEmbed)
                        
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            overwrite.read_messages = True
            await channel.set_permissions(sRole, overwrite=overwrite)




        async def addExp(self, helper, amount, guild, natural=True):
            global BASE_REWARD
            
            cur.execute(f"SELECT * FROM helpLevels WHERE memberId = {helper.id} AND guildId = {guild.id}")
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
                    cur.execute(f"SELECT roleId FROM helpRoles WHERE guildId = {guild.id} ORDER BY level ASC")
                    roles = cur.fetchall()
                    
                    if levelDifference >10:
                        removeIndex = int((baseLevel//10)-1)
                        index = int((level//10)-1)
                        removeRole = guild.get_role(int(roles[removeIndex][0]))
                        role = guild.get_role(int(roles[index][0]))
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



            cur.execute(f"UPDATE helpLevels SET XP = {exp}, peopleHelped = {helped}, level = {level} WHERE memberId = {helper.id}", )



        async def getRankImage(self,member: discord.Member, exp,  level, total, guild):
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

            
            cur.execute("SELECT level, roleId FROM helpRoles WHERE guildId = ? ORDER BY level DESC", (guild.id,))
            records = cur.fetchall()
            title = None
            for k, v in records:
                
                if k < level:
                    title = guild.get_role(v)
                    title = title.name
                    print(title)
            
                    continue
            if title is None:
                title = ""
            cur.execute(" SELECT level, memberId FROM helpLevels WHERE guildId = ? ORDER BY level DESC", (guild.id,))
            records = cur.fetchall()
            counter=1
            for k, v in records:
                if v == member.id:
                    position = counter
                    break
                counter+=1
            
            size = width, height = 900, 200
            image = Image.new("RGB", size, "#342e38")
            image = image.convert("RGBA")

            
            font = ImageFont.truetype("resources/fonts/impact.ttf",40)
            rankfont = ImageFont.truetype("resources/fonts/light.ttf",30)
            titlefont = ImageFont.truetype("resources/fonts/med.ttf",27)
            
            draw = ImageDraw.Draw(image)
            #draw.rounded_rectangle([10, 20, width-300, height-20], fill=(74,74,74, 355))
            draw.rounded_rectangle([10, 20, width-300, height-20], fill=(74,74,74, 200), width=3,radius=20)
            draw.rounded_rectangle([650, 20, width-30, height-20], fill=(74,74,74,200), width=3,radius=20)
            
            
            buffer_avatar = io.BytesIO()
            avatar_asset = member.avatar_url_as(format='jpg', size=128) # read JPG from server to buffer (file-like object)
            await avatar_asset.save(buffer_avatar) 
            buffer_avatar.seek(0)
            progress=exp/1000
            # read JPG from buffer to Image
            avatar_image = Image.open(buffer_avatar)
            avatar_image = avatar_image.resize((128,128))
            circle_image = Image.new("L", (128, 128))
            circle_draw = ImageDraw.Draw(circle_image)
            circle_draw.ellipse((0,0, 128,128), fill=255)
            image.paste(avatar_image, (20,35), circle_image)
            name = member.name + "#"+member.discriminator
            draw.multiline_text((175,35), name, font=font, fill=(0, 166, 255))
            draw.multiline_text((175,90), title, font=titlefont, fill=(0, 255, 242))
            draw.multiline_text((465,100), f"{exp}/1000", font=rankfont, fill=(164, 0, 252) )
            draw.multiline_text((662,50), f"RANK: #{position}", font=rankfont, fill=(0, 166, 255) ) 
            draw.multiline_text((662,90), f"Level: {level}", font=rankfont, fill=(0, 166, 255))
            draw.multiline_text((662,130), f"People helped: {total}", font=rankfont, fill=(0, 166, 255))
            draw = drawProgressBar(draw, 155,135, 400, 25, progress, )
            image.resize((1350,300))
            buffer_output = io.BytesIO()
            
            
            image.save(buffer_output, "PNG")
            buffer_output.seek(0)
            return buffer_output






    
def setup(bot):
    bot.add_cog(Help(bot))
