# PasteGit

PasteGit is a git-based pastebin.

All pastes are stored in git repositories, which has serveral advantages: 

- It doesn't use a database.
- You can easily change pastes manually, since they are just files.

Pastes can be edited and deleted by the original creator. Since we don't use a database, we use oauth to authenticate users.

## Setup

You will need to copy settings.example.py to settings.py, and you will need to change some settings. The comments inside this file should explain this.
