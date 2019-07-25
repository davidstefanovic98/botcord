# Joni-bot

## Description

JoniBot is envisioned to be an all round Discord bot with tons of random and not so random functionality.

## Features

- [x] GitHub integration
- [ ] Playing music
- [ ] Others

## Setup

Place your Discord token string like such in the root of the project.

`auth.cfg`

```
[auth]
token = tokenstring
```

Run the bot with:

```
python bot.py
```

## Usage

### GitHub

`$git sub/subscribe <email> <pass> <repo>` - Login and subscribe to a public repository on a given account. Message will be deleted in order to preserve privacy.

`$git unsub/unsubscribe` - Unsubscribe from the current repository.

`$git commits/commit [sha]` - Check last five commits or check a specific commit based on its sha hash.

`$git branches/branch [branch]` - Check all of the branches or a specific branch in the repository.

## Contributions

Ideas and suggestions are welcome.
