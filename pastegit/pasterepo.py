import os.path
import functools

from flask import render_template, session, flash, redirect, url_for, g
from git import Repo, NoSuchPathError, BadObject

from constants import LANGUAGES
import settings

class PasteRepo(Repo):
    """
    A subclass of Repo with some extra helper methods and properties.
    """

    def __init__(self, rid, rev='HEAD'):
        Repo.__init__(self, os.path.join(settings.REPO_DIR, str(rid)))

        # Store the repo id.
        self.id = rid
        try:
            self.rev = self.commit(rev)
        except BadObject:
            if rev == 'HEAD':
                self.rev = None
            else:
                raise

        # Determine the owner.
        if self.rev:
            cr = self.config_reader('repository')
            self.owner = {
                'email': cr.get('user', 'email'),
                'name': cr.get('user', 'name'),
            }
        else:
            self.owner = None

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
        if self.rev:
            self.commits = [self.commit('HEAD')]
            self.commits += [commit for commit in self.commits[0].iter_parents()]
        else:
            self.commits = []
        self.has_history = len(self.commits) > 1

        # Get the tags.
        self.has_releases = len(self.tags) > 0
        self.revtag = None
        if self.rev:
            for tag in self.tags:
                if tag.commit == self.rev:
                    self.revtag = tag
                    break

    def get_title(self):
        """
        Get the title of the main file from the given revision.
        """
        if not self.rev:
            raise Exception('Trying to get the title of a broken repo. Please fix or remove repo {}'.format(self.id))
        return self.rev.tree['title'].data_stream.read()

    def get_content(self):
        """
        Get the content of the main file from the given revision.
        """
        if not self.rev:
            raise Exception('Trying to get the content of a broken repo. Please fix or remove repo {}'.format(self.id))
        return self.rev.tree[self.mainfile].data_stream.read()

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
        directory = os.path.join(settings.REPO_DIR, str(rid))
        Repo.init(directory)
        return PasteRepo(rid)

    @staticmethod
    def fetch(action='view'):
        """
        Wrapper for routes that will automatically grab the rid parameter and load
        the repo associated with it. If this fails an error message is displayed.

        Additionally, you can require the repo to be owned by the current user.
        """
        if action not in ('view', 'edit', 'delete'):
            raise AttributeException('{} is not a recognized action.'.format(action))

        def decorator(f):
            @functools.wraps(f)
            def wrapper(rid, rev='HEAD', *args, **kwargs):
                # Get the repo.
                try:
                    repo = PasteRepo(rid, rev=rev)
                except NoSuchPathError:
                    flash('That paste does not exist', 'danger')
                    return redirect(url_for('index'))
        
                # Check permission.
                if action == 'edit' and not g.user.can_edit(repo):
                    flash('You are not allowed to edit this paste', 'danger')
                    return redirect(url_for('view', rid=repo.id, rev=repo.rev.hexsha))
                elif action == 'delete' and not g.user.can_delete(repo):
                    flash('You are not allowed to delete this paste', 'danger')
                    return redirect(url_for('view', rid=repo.id, rev=repo.rev.hexsha))

                return f(repo=repo, *args, **kwargs)
            return wrapper
        return decorator
