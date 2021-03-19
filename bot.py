from os import remove
from typing import List

import discord
from os.path import exists
from configparser import ConfigParser

from FileMessage import FileMessage
from colors import get_colors
from logger import init_system_logger

cfg_file_path = "auth.cfg"


class JoniBot(discord.Client):
	token = None

	def __init__(self, *args, **kwargs):
		self.config = ConfigParser()
		self.load_config()
		super().__init__(**kwargs)

		init_system_logger()

		self.run(self.token)

	async def on_ready(self):
		print('Logged on as {0}!'.format(self.user))

	async def on_message(self, message):
		if self.user == message.author:
			return

		if message.content.startswith("$"):
			await self.do_command(message)
			return

		await self.send_colors(message)

	async def do_command(self, message):
		pass

	async def do_send_files(self, channel, files: List[FileMessage]):
		for file in files:
			await channel.send(file.message, file=file.file)

	def load_config(self):
		if exists(cfg_file_path):
			self.config.read(cfg_file_path)
		else:
			raise FileExistsError("Config file auth.cfg not found in root directory")

		if "auth" in self.config and "token" in self.config["auth"]:
			self.token = self.config["auth"]["token"]
		else:
			raise IOError("Token not found in auth.cfg file")

	async def send_colors(self, message):
		colors = get_colors(message.content)
		print(colors)
		files = list(map(lambda c: FileMessage(c[0], c[1]), colors))
		await self.do_send_files(message.channel, files)


if __name__ == '__main__':
	client = JoniBot()
