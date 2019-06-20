import json

import requests


class GitApi(object):
	def __init__(self, user=None, passwd=None, repo=None) -> None:
		super().__init__()
		if user is None or passwd is None or repo is None:
			raise IOError("Invalid arguments")
		self.user = user
		self.passwd = passwd
		self.repo = repo

	def get_commit(self, sha=None) -> str:
		if sha is not None:
			url = "https://api.github.com/repos/{user}/{repo}/commits/{sha}".format(user=self.user, passwd=self.passwd,
			                                                                        repo=self.repo, sha=sha)
		else:
			url = "https://api.github.com/repos/{user}/{repo}/commits".format(user=self.user, passwd=self.passwd,
			                                                                  repo=self.repo)

		response = requests.get(url, auth=(self.user, self.passwd),
		                        params={"username": self.user, "password": self.passwd})

		if response.status_code == 422:
			return "**Not a valid commit hash**"
		elif response.status_code == 404:
			return "**Repository not found**"
		elif response.status_code != 200:
			return "**Something went wrong _" + str(response.status_code) + "_**"

		data = json.loads(response.content)
		message = ""

		if sha is not None:
			message += "Author: **{}** ({})\n".format(data["commit"]["author"]["name"], data["author"]["login"])
			message += "Message: {}\n".format(data["commit"]["message"])
			message += "Date: {}\n".format(data["commit"]["author"]["date"])
			message += "URL: <{}>\n".format(data["html_url"])
			message += "Files changed: \n\n"
			for file in data["files"]:
				message += "Path: " + file["filename"] + "\n"
				message += "Status: " + file["status"] + "\n"
				message += "Changes: " + str(file["changes"]) + "\n\n"

			return message
		else:
			message += "Latest 5 commits to any branch: \n\n"
			for i in range(0, 5):
				commit = data[i]
				message += "Author: **{}** ({})\n".format(commit["commit"]["author"]["name"], commit["author"]["login"])
				message += "Message: {}\n".format(commit["commit"]["message"])
				message += "sha: _{}_\n".format(commit["sha"])
				message += "URL: _{}_\n\n".format(commit["html_url"])
			return message

	def get_branch(self, branch=None) -> str:
		if branch is not None:
			url = "https://api.github.com/repos/{user}/{repo}/branches/{branch}".format(user=self.user, repo=self.repo,
			                                                                            branch=branch)
		else:
			url = "https://api.github.com/repos/{user}/{repo}/branches".format(user=self.user, repo=self.repo)

		print(self.user, self.passwd)
		response = requests.get(url, auth=(self.user, self.passwd),
		                        params={"username": self.user, "password": self.passwd})

		if response.status_code == 422:
			return "**Not a valid branch**"
		elif response.status_code == 404:
			return "**Repository not found**"
		elif response.status_code != 200:
			return "**Something went wrong _" + str(response.status_code) + "_**"

		data = json.loads(response.content)
		message = ""

		if branch is None:
			message += "List of all active branches:\n\n"
			for b in data:
				message += "Branch: **" + b["name"] + "**\n"
				message += "SHA: _" + b["commit"]["sha"] + "_\n\n"
			return message
		else:
			message += "Branch: **" + data["name"] + "**\n"
			message += "Latest commit: **" + data["commit"]["commit"]["message"] + "**\n"
			message += "SHA: _" + data["commit"]["sha"] + "_\n"
			message += "URL: _" + data["commit"]["html_url"] + "_ \n\n"
			return message
