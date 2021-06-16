import re
from datetime import datetime, timedelta

joins = {}


async def member_join_notify(member, before, after, channels):
	channel = after.channel
	match = re.search("(\\w+)-voice.*", channel.name)
	prefix = match.group(1)
	dest_channel = list(filter(lambda x: x.name.startswith(prefix + "-text"), channels))[0]

	member_id = str(member.id) + "-" + after.channel.name
	last_join_time = joins.get(member_id)
	if last_join_time is None:
		joins[member_id] = datetime.now()
	else:
		if (last_join_time + timedelta(minutes=10)) > datetime.now():
			return

	if dest_channel is not None and before.channel is None:
		await dest_channel.send(f"**{member.name.split('#')[0]}** joined **{after.channel.name}** 🖐")
	print(joins)
