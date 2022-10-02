print("Hello World")

import interactions
import math
import time

class Profile(interactions.Extension):

	#Initialises the bot
	def __init__(self, bot):
		self.bot = bot;

	#Creates the poll command
	@interactions.extension_command(
		name="poll",
		description="Create a poll with up to 54 options. seperate options with ;",
		options=[
			interactions.Option(
				name="question",
				description="Write a question for people to respond to",
				type=interactions.OptionType.STRING,
				required=True
			),
			interactions.Option(
				name="options",
				description="Up to 54 options, seperated by ;, allows spaces eg: options: option 1;option 2",
				type=interactions.OptionType.STRING,
				required=True
				)
			]
		)
	#awaits poll command
	async def poll(self, ctx: interactions.CommandContext, question: str, options: str):
		print("Recieved poll command with {} as options".format(str(options)))
		counter = 0
		#splits options into a list
		items = str(options).split(';')
		#list of emoji the bot is allowed to react with
		emojibank = [':zero:', ':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:', ':regional_indicator_a:', ':regional_indicator_b:', ':regional_indicator_c:', ':regional_indicator_d:', ':regional_indicator_e:', ':regional_indicator_f:', ':regional_indicator_g:', ':regional_indicator_h:', ':regional_indicator_i:', ':regional_indicator_j:', ':regional_indicator_k:', ':regional_indicator_l:', ':regional_indicator_m:', ':regional_indicator_n:', ':regional_indicator_o:', ':regional_indicator_p:', ':regional_indicator_q:', ':regional_indicator_r:', ':regional_indicator_s:', ':regional_indicator_t:', ':regional_indicator_u:', ':regional_indicator_v:', ':regional_indicator_w:', ':regional_indicator_x:', ':regional_indicator_y:', ':regional_indicator_z:', ':white_circle:', ':black_circle:', ':red_circle:', ':blue_circle:', ':brown_circle:', ':purple_circle:', ':green_circle:', ':yellow_circle:', ':orange_circle:', ':white_large_square:', ':black_large_square:', ':red_square:', ':blue_square:', ':brown_square:', ':purple_square:', ':green_square:', ':yellow_square:', ':orange_square:']
		emojicodes = ["0\ufe0f\u20e3", "1\ufe0f\u20e3", "2\ufe0f\u20e3", "3\ufe0f\u20e3", "4\ufe0f\u20e3", "5\ufe0f\u20e3", "6\ufe0f\u20e3", "7\ufe0f\u20e3", "8\ufe0f\u20e3", "9\ufe0f\u20e3", "🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿", "\u26aa", "\u26ab", "🔴", "🔵", "🟤", "🟣", "🟢", "🟡", "🟡", "\u2b1c", "\u2b1b", "🟥", "🟦", "🟫", "🟪", "🟩", "🟨", "🟧"]
		#holds the current message contents
		currentmessage = ""
		content = ""
		#finds the number of parts needed to have only 20 items per message, this is due to discord limits
		parts = math.ceil(len(items) / 20)
		#attempts to create the embed with options and add reactions
		try:
			for pt in range(0, parts):
				limit = (20 * pt) + 20
				if limit > len(items):
					limit = len(items)
				for i in range((20 * pt), limit):
					content += emojibank[i] + " " + items[i] + "\n"
				embed = interactions.Embed(
					title=f"Poll: {question} | Part {str(pt + 1)} of {str(parts)}",
					description=str(content)
				)
				embed.set_footer("Strawpoll Module Created by CoronaBorealis#6969")
				content = ""
				currentmessage = await ctx.send(embeds=embed)
				for i in range((20 * pt), limit):
					await currentmessage.create_reaction(emojicodes[i])
					time.sleep(0.1)
		except:
			await ctx.send("Looks like something broke! Maybe you somehow needed more than 54 options? Sorry. My bot can't handle that large of a poll. Maybe consider using Google Forms instead: https://www.google.com/forms/about/")

def setup(bot):
    Profile(bot)
