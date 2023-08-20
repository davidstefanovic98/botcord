from typing import List

import discord
from os.path import exists
from configparser import ConfigParser

from FileMessage import FileMessage
from colors import get_colors
from gitapi import GitApi
from logger import init_system_logger
from member import member_join_notify

cfg_file_path = "auth.cfg"


class Botcord(discord.Client):
    token = None
    channels = []
    subs = {}
    webhooks = {}

    def __init__(self):
        self.config = ConfigParser()
        self.load_config()
        super().__init__(intents=discord.Intents(messages=True,
                                                 message_content=True,
                                                 voice_states=True,
                                                 members=True,
                                                 guilds=True,
                                                 webhooks=True))

        init_system_logger()

        self.run(self.token)

    async def on_voice_state_update(self, member, before, after):
        await member_join_notify(member, before, after, self.channels)

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        self.channels = [x for x in self.get_all_channels()]

    async def on_message(self, message):
        if self.user == message.author:
            return

        if message.content.startswith("$"):
            await self.do_command(message)
            return

        await self.send_colors(message)

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
        if len(args) == 4:
            user = args[2]
            repo = args[3]
            user_id = str(message.author.id)
            self.subs[user_id] = {}
            self.subs[user_id]["user"] = user
            self.subs[user_id]["repo"] = repo
            git = GitApi(self.subs[user_id]["user"],
                         self.subs[user_id]["repo"])
            await message.delete()
            list_of_webhooks = await message.channel.webhooks()
            webhooks = {webhook.name: webhook for webhook in list_of_webhooks}
            name = "{}-webhook".format(repo)
            if name not in webhooks:
                webhook = await message.channel.create_webhook(name=name)
                git.create_git_webhook(webhook.url)
            await message.channel.send("**GG, {} subscribed to {} github repository**".format(user, repo))

        else:
            await message.delete()
            await message.channel.send("**Invalid subscription arguments**")

    async def unsubscribe(self, message):
        user_id = str(message.author.id)
        repo = self.subs[user_id]["repo"]
        git = GitApi(self.subs[user_id]["user"],
                     self.subs[user_id]["repo"])

        del self.subs[user_id]
        await message.delete()
        channel_webhooks = await message.channel.webhooks()
        github_webhooks = git.get_all_webhooks()
        for webhook in channel_webhooks:
            for github_webhook in github_webhooks:
                modified_url = github_webhook["config"]["url"].replace("/github", "")
                if modified_url == webhook.url:
                    await webhook.delete()
                    git.delete_git_webhook(github_webhook["id"])
                    break

        await message.channel.send("**{} unsubscribed from {}**".format(message.author, repo))

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
    client = Botcord()
