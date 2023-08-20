import json
import requests
import jwt
import time
import sys


class GitApi(object):
    def __init__(self, user=None, repo=None) -> None:
        super().__init__()
        if user is None or repo is None:
            raise IOError("Invalid arguments")
        self.user = user
        self.repo = repo

    def get_commit(self, sha=None) -> str:
        if sha is not None:
            url = "https://api.github.com/repos/{user}/{repo}/commits/{sha}".format(user=self.user,
                                                                                    repo=self.repo, sha=sha)
        else:
            url = "https://api.github.com/repos/{user}/{repo}/commits".format(user=self.user,
                                                                              repo=self.repo)

        jwt_token = self.create_jwt_token()
        installation_id = self.get_installation_id(jwt_token)
        access_token = self.get_access_token(installation_id, jwt_token)
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {access_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        response = requests.get(url=url, headers=headers)

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

        jwt_token = self.create_jwt_token()
        installation_id = self.get_installation_id(jwt_token)
        access_token = self.get_access_token(installation_id, jwt_token)
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {access_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        response = requests.get(url=url, headers=headers)

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

    def create_git_webhook(self, url_for_discord):
        url = "https://api.github.com/repos/{user}/{repo}/hooks".format(user=self.user, repo=self.repo)

        data = {
            "name": "web",
            "config": {
                "url": f"{url_for_discord}/github",
                "content_type": "json",
                "insecure_ssl": '0'
            },
            "events": ["push"]
        }
        jwt_token = self.create_jwt_token()
        installation_id = self.get_installation_id(jwt_token)
        access_token = self.get_access_token(installation_id, jwt_token)
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {access_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        response = requests.post(url=url, json=data, headers=headers)

    def create_jwt_token(self):
        app_id = 378356
        # Open PEM
        with open("/home/david/.certs/github/botcord-app.2023-08-20.private-key.pem", 'rb') as pem_file:
            signing_key = jwt.jwk_from_pem(pem_file.read())

        payload = {
            # Issued at time
            'iat': int(time.time()),
            # JWT expiration time (10 minutes maximum)
            'exp': int(time.time()) + 600,
            # GitHub App's identifier
            'iss': app_id
        }

        # Create JWT
        jwt_instance = jwt.JWT()
        encoded_jwt = jwt_instance.encode(payload, signing_key, alg='RS256')
        return encoded_jwt

    def get_installation_id(self, token):
        url = "https://api.github.com/repos/{user}/{repo}/installation".format(user=self.user, repo=self.repo)
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        response = requests.get(url=url, headers=headers)
        return json.loads(response.content.decode("utf-8"))["id"]

    def get_access_token(self, id, token):
        url = "https://api.github.com/app/installations/{id}/access_tokens".format(id=id)
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        response = requests.post(url=url, headers=headers)
        return json.loads(response.content.decode("utf-8"))["token"]

    def delete_git_webhook(self, id):
        url = "https://api.github.com/repos/{user}/{repo}/hooks/{id}".format(user=self.user, repo=self.repo, id=id)
        token = self.create_jwt_token()
        installation_id = self.get_installation_id(token)
        access_token = self.get_access_token(installation_id, token)
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {access_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        requests.delete(url=url, headers=headers)

    def get_all_webhooks(self):
        url = "https://api.github.com/repos/{user}/{repo}/hooks".format(user=self.user, repo=self.repo)
        token = self.create_jwt_token()
        installation_id = self.get_installation_id(token)
        access_token = self.get_access_token(installation_id, token)
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {access_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        response = requests.get(url=url, headers=headers)
        return json.loads(response.content.decode("utf-8"))