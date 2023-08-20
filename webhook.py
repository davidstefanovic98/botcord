"""
    After subscribing to some repo, bot should be able to create webhook on github and discord as well.
"""


class GithubWebhook:
    def __init__(self, id=None) -> None:
        super().__init__()
        self.id = id

