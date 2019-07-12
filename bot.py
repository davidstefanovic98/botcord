import discord
from gitapi import GitApi
from os.path import exists
from configparser import ConfigParser

cfgfilepth = "auth.cfg"


class JoniBot(discord.Client):
	config = ConfigParser()
	token = None
	subs = {}

	def __init__(self, *args, **kwargs):
		if exists(cfgfilepth):
			self.config.read(cfgfilepth)
		else:
			raise FileExistsError("Config file auth.cfg not found in root directory")

		if "auth" in self.config and "token" in self.config["auth"]:
			self.token = self.config["auth"]["token"]
		else:
			raise IOError("Token not found in auth.cfg file")
		super().__init__(**kwargs)

		self.run(self.token)

	async def on_ready(self):
		print('Logged on as {0}!'.format(self.user))

	async def on_message(self, message):
		if self.user == message.author:
			return

		if message.content.startswith("$"):
			await self.do_command(message)

	async def do_command(self, message):
		args = message.content[1:].split(" ")
		if args[0] == "git":
			if args[1] == "sub" or args[1] == "subscribe":
				await self.subscribe(message)
				return
			elif args[1] == "unsub" or args[1] == "unsubscribe":
				await self.unsubscribe(message)
				return

			user_id = str(message.author.id)

			if user_id not in self.subs:
				await message.channel.send("**You are not subscribed to a repository**")
				return

			try:
				git = GitApi(self.subs[user_id]["user"],
				             self.subs[user_id]["passwd"],
				             self.subs[user_id]["repo"])
			except IOError:
				await message.channel.send("**You are not subscribed to a repository**")
				return

			if args[1] == "commits" or args[1] == "commit":

				if len(args) == 3:
					await message.channel.send(git.get_commit(args[2]))

				elif len(args) == 2:
					await message.channel.send(git.get_commit())

			if args[1] == "branches" or args[1] == "branch":

				if len(args) == 3:
					await message.channel.send(git.get_branch(args[2]))

				elif len(args) == 2:
					await message.channel.send(git.get_branch())

	async def subscribe(self, message):
		args = message.content[1:].split(" ")
		if len(args) == 5:
			user = args[2]
			passwd = args[3]
			repo = args[4]
			user_id = str(message.author.id)
			self.subs[user_id] = {}
			self.subs[user_id]["user"] = user
			self.subs[user_id]["passwd"] = passwd
			self.subs[user_id]["repo"] = repo
			await message.delete()
			await message.channel.send("**GG, {} subscribed to {} github repository**".format(user, repo))
		else:
			await message.delete()
			await message.channel.send("**Invalid subscription arguments**")

	async def unsubscribe(self, message):
		user_id = str(message.author.id)
		repo = self.subs[user_id]["repo"]
		del self.subs[user_id]
		await message.delete()
		await message.channel.send("**{} unsubscribed fron {}**".format(message.author, repo))


client = JoniBot()
