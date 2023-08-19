import re
from datetime import datetime, timedelta

from discord import Embed

joins = {}


async def member_join_notify(member, before, after, channels):
	match = re.search("(\\w+)-voice.*", after.channel.name)
	prefix = match.group(1)
	dest_channel = list(filter(lambda x: x.name.startswith(prefix + "-joined"), channels))[0]
	member_id = str(member.id) + "-" + after.channel.name
	last_join_time = joins.get(member_id)
	if last_join_time is None:
		joins[member_id] = datetime.now()
	else:
		if (last_join_time + timedelta(minutes=10)) > datetime.now():
			return

	if dest_channel is not None and before.channel is None:
		try:
			embed = Embed()
			embed.title = f"**{member.display_name}** joined **{after.channel.name}** 🖐"
			embed.set_thumbnail(url=member.avatar)
			embed.set_author(name="Botcord")
			embed.timestamp = datetime.now()
			embed.colour = member.colour
			await dest_channel.send(embed=embed)
		except Exception as e:
			print(e)
	print(joins)
