import discord


class FileMessage(object):
	def __init__(self, message ,file):
		self.message = ""
		self.file = discord.File(file)
