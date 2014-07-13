# PasteGit

PasteGit is a git-based pastebin.

All pastes are stored in git repositories, which means you can easily change many things (content, history, releases) manually, since it's just a git repo with a few files in it.

Authentication is done through OAuth. By default it supports Google and Facebook, but it's trivial to add more providers.

Because of this it's completely database-less, so all you need is a webserver than can run python.

If you're good with git you can also do things such as rewrite history much easier and in a more flexible and powerfull manner than with a database-driven solution.

It's very flexible, see the settings.example.py file for a list of settings and an explanation about what they do.

## Installation

    git clone https://github.com/MaienM/PasteGit.git 
	cd PasteGit
	bower install
	cp settings.example.py settings.py

Then just edit settings.py to your liking, and enjoy!
