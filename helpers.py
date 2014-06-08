import os.path
import functools
import time

import babel.dates
from flask import render_template, session
from git import Repo, NoSuchPathError

from constants import LANGUAGES
import settings

class PasteRepo(Repo):
    """
    A subclass of Repo with some extra helper methods and properties.
    """

    def __init__(self, rid):
        Repo.__init__(self, os.path.join(settings.REPODIR, str(rid)))

        # Store the repo id.
        self.id = rid

        # Determine whether the currently logged in user is the owner.
        try:
            assert session['user']['email'] == self.config_reader('repository').get('user', 'email')
            self.are_owner = True
        except:
            self.are_owner = False

        # Determine what the main file is.
        self.mainfile = None
        self.files = [entry[0] for entry in self.index.entries.keys()]
        if self.files:
            self.files.remove('title')
            self.mainfile = self.files[0]

        # Determine the language of the main file.
        self.language = None
        if self.mainfile:
            ext = '.' + self.mainfile.rsplit('.')[-1]
            for lang in LANGUAGES.values():
                if ext in lang['extensions']:
                    self.language = lang
                    break

        # Get the commits.
        self.commits = [self.commit('HEAD')]
        self.commits += [commit for commit in self.commits[0].iter_parents()]

    def get_title(self, rev='HEAD'):
        """
        Get the title of the main file from the given revision.
        """
        return self.commit(rev).tree['title'].data_stream.read()

    def get_content(self, rev='HEAD'):
        """
        Get the content of the main file from the given revision.
        """
        return self.commit(rev).tree[self.mainfile].data_stream.read()

    def update(self, message, title, content):
        """
        Update the repo with a new version.
        """
        with open(os.path.join(self.working_dir, 'title'), 'w') as f:
            f.write(title)
        with open(os.path.join(self.working_dir, self.mainfile), 'w') as f:
            f.write(content)
        self.index.add(['title', self.mainfile])
        self.index.write()
        self.index.commit(message)

    @staticmethod
    def init(rid):
        """
        Initialize a new repository.
        """
        directory = os.path.join(settings.REPODIR, str(rid))
        Repo.init(directory)
        return PasteRepo(rid)

def fetch_repo(f):
    """
    Wrapper for routes that will automatically grab the rid parameter and load
    the repo associated with it. If this fails, it will render the error template.
    """
    @functools.wraps(f)
    def wrapper(rid, *args, **kwargs):
        try:
            repo = PasteRepo(rid)
        except NoSuchPathError:
            return render_template('error.html', error='That paste does not exist')
        return f(repo=repo, *args, **kwargs)
    return wrapper

def require_repo_owner(f):
    """
    Require the current user to be the owner of the repo. If this is not the
    case, the error template will be rendered.
    """
    @functools.wraps(f)
    def wrapper(repo, *args, **kwargs):
        if repo.are_owner:
            return f(repo=repo, *args, **kwargs)
        else:
            return render_template('error.html', error='You are not the owner of this paste')
    return wrapper

def timedelta(ts):
    """
    Transform a timestamp into a time delta (8 minutes ago, etc).
    This is a Jinja2 filter.
    """
    return babel.dates.format_timedelta(time.time() - ts)
